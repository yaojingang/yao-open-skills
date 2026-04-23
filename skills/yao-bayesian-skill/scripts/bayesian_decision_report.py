#!/usr/bin/env python3
import argparse
import bisect
import json
import math
import sys
from pathlib import Path


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def round_float(value: float | None, digits: int = 4) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def normalize_value(value):
    if isinstance(value, float):
        return round_float(value)
    if isinstance(value, int):
        return value
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_value(item) for key, item in value.items()}
    return value


def localize_text(value, lang: str = "zh") -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):
        key_groups = {
            "zh": ("zh", "zh-CN", "zh_cn", "cn"),
            "en": ("en", "en-US", "en_us"),
        }
        for key in key_groups.get(lang, ()):
            text = value.get(key)
            if isinstance(text, str) and text.strip():
                return text.strip()
        for fallback in ("zh", "zh-CN", "en", "en-US"):
            text = value.get(fallback)
            if isinstance(text, str) and text.strip():
                return text.strip()
        for text in value.values():
            if isinstance(text, str) and text.strip():
                return text.strip()
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, str):
        return value
    return str(value)


def localize_list(values, lang: str = "zh") -> list[str]:
    return [localize_text(item, lang) for item in (values or []) if localize_text(item, lang)]


def confidence_label_zh(code: str | None) -> str | None:
    mapping = {
        "low": "低",
        "medium": "中",
        "medium-high": "中高",
    }
    return mapping.get(code, code)


def direction_label_zh(direction: str | None) -> str:
    mapping = {
        "support": "支持",
        "against": "削弱",
    }
    return mapping.get(direction or "", direction or "未知")


def load_request(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_output(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def log_beta_fn(alpha: float, beta: float) -> float:
    return math.lgamma(alpha) + math.lgamma(beta) - math.lgamma(alpha + beta)


def beta_quantiles_grid(alpha: float, beta: float, probs: tuple[float, float] = (0.05, 0.95), steps: int = 4000) -> list[float]:
    if alpha <= 0 or beta <= 0:
        raise ValueError("alpha and beta must be positive")
    xs = [(index + 0.5) / steps for index in range(steps)]
    log_norm = log_beta_fn(alpha, beta)
    log_weights = []
    for x in xs:
        log_pdf = (alpha - 1.0) * math.log(x) + (beta - 1.0) * math.log(1.0 - x) - log_norm
        log_weights.append(log_pdf)
    max_log = max(log_weights)
    weights = [math.exp(item - max_log) for item in log_weights]
    total = sum(weights)
    cdf = []
    running = 0.0
    for weight in weights:
        running += weight / total
        cdf.append(running)
    quantiles = []
    for prob in probs:
        idx = bisect.bisect_left(cdf, prob)
        idx = min(idx, steps - 1)
        quantiles.append(xs[idx])
    return quantiles


def beta_stats(alpha: float, beta: float) -> dict:
    mean = alpha / (alpha + beta)
    low, high = beta_quantiles_grid(alpha, beta)
    return {
      "mean": mean,
      "credible_interval": [low, high],
      "equivalent_sample_size": alpha + beta,
    }


def build_prior(prior: dict, warnings: list[str]) -> dict:
    alpha = prior.get("alpha")
    beta = prior.get("beta")
    probability = prior.get("probability")
    ess = prior.get("equivalent_sample_size")

    if alpha is not None and beta is not None:
        alpha = float(alpha)
        beta = float(beta)
        stats = beta_stats(alpha, beta)
        if probability is None:
            probability = stats["mean"]
        if ess is None:
            ess = alpha + beta
        return {
            "mode": "beta",
            "alpha": alpha,
            "beta": beta,
            "probability": float(probability),
            "equivalent_sample_size": float(ess),
            "credible_interval": stats["credible_interval"],
            "source_summary": localize_list(prior.get("source_summary", []), "zh"),
            "source_quality": localize_text(prior.get("source_quality"), "zh"),
            "confidence": confidence_label_zh(localize_text(prior.get("confidence"), "zh")),
        }

    if probability is None:
        raise ValueError("prior must include either alpha/beta or probability")

    probability = clamp(float(probability), 1e-6, 1 - 1e-6)
    payload = {
        "mode": "probability",
        "probability": probability,
        "equivalent_sample_size": float(ess) if ess is not None else None,
        "source_summary": localize_list(prior.get("source_summary", []), "zh"),
        "source_quality": localize_text(prior.get("source_quality"), "zh"),
        "confidence": confidence_label_zh(localize_text(prior.get("confidence"), "zh")),
    }
    if ess is not None:
        alpha = probability * float(ess)
        beta = (1 - probability) * float(ess)
        if alpha > 0 and beta > 0:
            stats = beta_stats(alpha, beta)
            payload.update(
                {
                    "mode": "beta",
                    "alpha": alpha,
                    "beta": beta,
                    "credible_interval": stats["credible_interval"],
                }
            )
    else:
        warnings.append("未提供先验等效样本量，先验强度相关的敏感性判断会更弱。")
    return payload


def effective_lr(item: dict) -> float:
    lr = float(item.get("likelihood_ratio", 1.0))
    if lr <= 0:
        raise ValueError(f"likelihood_ratio must be positive for evidence item {item.get('name', '<unnamed>')}")
    direction = item.get("direction", "support")
    if direction == "against":
        lr = 1.0 / lr
    discount = clamp(float(item.get("dependency_discount", 1.0)), 0.0, 1.0)
    return math.exp(math.log(lr) * discount)


def apply_odds_update(prior_probability: float, evidence: list[dict], lr_power: float = 1.0) -> tuple[float, list[dict], float, float]:
    prior_probability = clamp(prior_probability, 1e-6, 1 - 1e-6)
    prior_odds = prior_probability / (1.0 - prior_probability)
    odds = prior_odds
    log = []
    for item in evidence:
        base_effective_lr = effective_lr(item)
        effective_with_power = math.exp(math.log(base_effective_lr) * lr_power)
        before = odds
        odds *= effective_with_power
        log.append(
            {
                "name": item.get("name"),
                "quality": item.get("quality"),
                "direction": item.get("direction", "support"),
                "base_likelihood_ratio": round_float(float(item.get("likelihood_ratio", 1.0))),
                "dependency_discount": round_float(float(item.get("dependency_discount", 1.0))),
                "effective_likelihood_ratio": round_float(base_effective_lr),
                "lr_power": round_float(lr_power),
                "applied_likelihood_ratio": round_float(effective_with_power),
                "odds_before": round_float(before),
                "odds_after": round_float(odds),
            }
        )
    posterior_probability = odds / (1.0 + odds)
    return posterior_probability, log, prior_odds, odds


def apply_beta_binomial(prior_payload: dict, observations: dict) -> dict:
    alpha = float(prior_payload["alpha"])
    beta = float(prior_payload["beta"])
    trials = int(observations["trials"])
    successes = int(observations["successes"])
    failures = trials - successes
    if successes < 0 or failures < 0:
        raise ValueError("observations.successes must be between 0 and observations.trials")
    post_alpha = alpha + successes
    post_beta = beta + failures
    stats = beta_stats(post_alpha, post_beta)
    return {
        "posterior_alpha": post_alpha,
        "posterior_beta": post_beta,
        "posterior_probability": stats["mean"],
        "credible_interval": stats["credible_interval"],
        "calculation_log": [
            {
                "step": "prior",
                "alpha": round_float(alpha),
                "beta": round_float(beta),
            },
            {
                "step": "data",
                "trials": trials,
                "successes": successes,
                "failures": failures,
            },
            {
                "step": "posterior",
                "alpha": round_float(post_alpha),
                "beta": round_float(post_beta),
            },
        ],
    }


def update_interval_with_evidence(interval: list[float], evidence: list[dict]) -> list[float]:
    updated = [apply_odds_update(value, evidence)[0] for value in interval]
    return sorted(updated)


def default_prior_scenarios(prior_payload: dict) -> list[float]:
    if prior_payload.get("mode") == "beta":
        alpha = float(prior_payload["alpha"])
        beta = float(prior_payload["beta"])
        low, high = beta_quantiles_grid(alpha, beta, probs=(0.1, 0.9))
        base = float(prior_payload["probability"])
        return sorted({round(low, 4), round(base, 4), round(high, 4)})
    base = float(prior_payload["probability"])
    low = clamp(base * 0.6, 0.01, 0.99)
    high = clamp(max(base * 1.4, base + 0.1), 0.01, 0.99)
    return sorted({round(low, 4), round(base, 4), round(high, 4)})


def utilities_for_action(action: dict) -> tuple[float, float]:
    if "utility_if_h_true" in action and "utility_if_h_false" in action:
        return float(action["utility_if_h_true"]), float(action["utility_if_h_false"])
    cost = float(action.get("cost", 0.0))
    upside_if_true = float(action.get("upside_if_h_true", 0.0))
    downside_if_false = float(action.get("downside_if_h_false", 0.0))
    opportunity_cost = float(action.get("opportunity_cost", 0.0))
    utility_true = upside_if_true - cost + opportunity_cost
    utility_false = downside_if_false - cost + opportunity_cost
    return utility_true, utility_false


def action_threshold(utility_true: float, utility_false: float) -> float | None:
    delta = utility_true - utility_false
    if abs(delta) < 1e-12:
        return None
    threshold = -utility_false / delta
    if threshold < 0:
        return 0.0
    if threshold > 1:
        return 1.0
    return threshold


def evaluate_actions(actions: list[dict], posterior_probability: float) -> list[dict]:
    evaluated = []
    for action in actions:
        utility_true, utility_false = utilities_for_action(action)
        expected_value = posterior_probability * utility_true + (1.0 - posterior_probability) * utility_false
        threshold = action_threshold(utility_true, utility_false)
        evaluated.append(
            {
                "name": action["name"],
                "utility_if_h_true": round_float(utility_true),
                "utility_if_h_false": round_float(utility_false),
                "expected_value": round_float(expected_value),
                "action_threshold": round_float(threshold),
            }
        )
    evaluated.sort(key=lambda item: item["expected_value"], reverse=True)
    return evaluated


def recommendation_confidence(warnings: list[str], stability: str, evidence: list[dict]) -> str:
    weak_count = sum(1 for item in evidence if item.get("quality") in {"D", "E"})
    if stability == "unstable" or len(warnings) >= 3 or weak_count >= 2:
        return "low"
    if stability == "mixed" or len(warnings) >= 1 or weak_count >= 1:
        return "medium"
    return "medium-high"


def natural_frequency(prior_probability: float, posterior_probability: float, base: int = 100) -> dict:
    prior_cases = round(prior_probability * base)
    posterior_cases = round(posterior_probability * base)
    return {
        "base_population": base,
        "prior_expected_successes": prior_cases,
        "posterior_expected_successes": posterior_cases,
        "explanation": (
            f"在 {base} 个相似案例里，先验大约意味着其中 {prior_cases} 个会成功。"
            f"加入当前证据后，估计会成功的案例约为 {posterior_cases} 个。"
        ),
    }


def information_value_hint(actions: list[dict], posterior_probability: float, candidates: list[str]) -> dict:
    best = actions[0] if actions else None
    second = actions[1] if len(actions) > 1 else None
    gap = None
    if best and second:
        gap = float(best["expected_value"]) - float(second["expected_value"])
    near_threshold = False
    if best and best.get("action_threshold") is not None:
        near_threshold = abs(posterior_probability - float(best["action_threshold"])) <= 0.1
    high_value = near_threshold or (gap is not None and abs(gap) <= max(5000.0, abs(float(best["expected_value"])) * 0.15))
    candidate = candidates[0] if candidates else None
    if candidate is None:
        candidate = "优先收集一个比口头兴趣更接近真实行为的低成本信号。"
    return {
        "high_value": high_value,
        "recommended_next_information": candidate,
        "reason": (
            "当前结果已经接近关键行动阈值，新增信息有较大概率改变建议。"
            if high_value
            else "继续补充信息仍然有价值，但当前建议对边界变化没有那么敏感。"
        ),
    }


def build_sensitivity(method: str, prior_payload: dict, evidence: list[dict], actions: list[dict], observations: dict | None, sensitivity: dict) -> dict:
    prior_scenarios = sensitivity.get("prior_probabilities") or default_prior_scenarios(prior_payload)
    prior_scenarios = [clamp(float(value), 1e-6, 1 - 1e-6) for value in prior_scenarios]
    lr_power_factors = sensitivity.get("lr_power_factors") or [0.75, 1.0, 1.25]
    lr_power_factors = [float(value) for value in lr_power_factors]

    scenario_results = []
    recommended_actions = []
    for prior_probability in prior_scenarios:
        if method.startswith("beta-binomial") and prior_payload.get("mode") == "beta" and observations is not None:
            ess = float(prior_payload["equivalent_sample_size"])
            alpha = prior_probability * ess
            beta = (1.0 - prior_probability) * ess
            posterior = apply_beta_binomial({"alpha": alpha, "beta": beta}, observations)
            base_probability = posterior["posterior_probability"]
            if evidence:
                for lr_power in lr_power_factors:
                    posterior_probability, _, _, _ = apply_odds_update(base_probability, evidence, lr_power=lr_power)
                    evaluated = evaluate_actions(actions, posterior_probability) if actions else []
                    recommended = evaluated[0]["name"] if evaluated else None
                    recommended_actions.append(recommended)
                    scenario_results.append(
                        {
                            "scenario_type": "combined",
                            "prior_probability": round_float(prior_probability),
                            "beta_binomial_probability": round_float(base_probability),
                            "lr_power": round_float(lr_power),
                            "posterior_probability": round_float(posterior_probability),
                            "recommended_action": recommended,
                        }
                    )
            else:
                posterior_probability = base_probability
                evaluated = evaluate_actions(actions, posterior_probability) if actions else []
                recommended = evaluated[0]["name"] if evaluated else None
                recommended_actions.append(recommended)
                scenario_results.append(
                    {
                        "scenario_type": "prior",
                        "prior_probability": round_float(prior_probability),
                        "posterior_probability": round_float(posterior_probability),
                        "credible_interval": [round_float(value) for value in posterior["credible_interval"]],
                        "recommended_action": recommended,
                    }
                )
        else:
            for lr_power in lr_power_factors:
                posterior_probability, _, _, _ = apply_odds_update(prior_probability, evidence, lr_power=lr_power)
                evaluated = evaluate_actions(actions, posterior_probability) if actions else []
                recommended = evaluated[0]["name"] if evaluated else None
                recommended_actions.append(recommended)
                scenario_results.append(
                    {
                        "scenario_type": "combined",
                        "prior_probability": round_float(prior_probability),
                        "lr_power": round_float(lr_power),
                        "posterior_probability": round_float(posterior_probability),
                        "recommended_action": recommended,
                    }
                )

    posterior_values = [float(item["posterior_probability"]) for item in scenario_results]
    unique_actions = {item for item in recommended_actions if item}
    if len(unique_actions) <= 1:
        stability = "stable"
    elif len(unique_actions) == 2:
        stability = "mixed"
    else:
        stability = "unstable"

    return {
        "scenarios": scenario_results,
        "posterior_range": [round_float(min(posterior_values)), round_float(max(posterior_values))],
        "conclusion_stability": {
            "stable": "稳定",
            "mixed": "混合",
            "unstable": "不稳定",
        }[stability],
        "conclusion_stability_code": stability,
    }


def choose_method(request: dict, prior_payload: dict) -> str:
    method = request.get("method", "auto")
    if method != "auto":
        return method
    observations = request.get("observations") or {}
    if observations.get("trials") is not None and observations.get("successes") is not None and prior_payload.get("mode") == "beta":
        return "beta-binomial"
    return "odds-update"


def build_report(request: dict) -> dict:
    warnings = []
    prior_payload = build_prior(request["prior"], warnings)
    method = choose_method(request, prior_payload)
    evidence = [
        {
            **item,
            "name": localize_text(item.get("name"), "zh"),
            "summary": localize_text(item.get("summary"), "zh"),
            "notes": localize_text(item.get("notes"), "zh"),
        }
        for item in request.get("evidence", [])
    ]
    actions = [
        {
            **item,
            "name": localize_text(item.get("name"), "zh"),
        }
        for item in request.get("actions", [])
    ]
    observations = request.get("observations") or None

    if method == "beta-binomial":
        if observations is None:
            raise ValueError("beta-binomial method requires observations.trials and observations.successes")
        posterior_block = apply_beta_binomial(prior_payload, observations)
        beta_posterior_probability = posterior_block["posterior_probability"]
        calculation_log = list(posterior_block["calculation_log"])
        posterior_probability = beta_posterior_probability
        posterior_interval = posterior_block["credible_interval"]
        prior_probability = float(prior_payload["probability"])
        if evidence:
            method = "beta-binomial+odds"
            posterior_probability, evidence_log, prior_odds, posterior_odds = apply_odds_update(beta_posterior_probability, evidence)
            posterior_interval = update_interval_with_evidence(posterior_interval, evidence)
            posterior_block.update(
                {
                    "beta_binomial_probability": beta_posterior_probability,
                    "prior_odds_before_evidence": prior_odds,
                    "posterior_odds_after_evidence": posterior_odds,
                    "posterior_probability": posterior_probability,
                    "credible_interval": posterior_interval,
                }
            )
            calculation_log.append(
                {
                    "step": "odds_update_after_beta_binomial",
                    "starting_probability": round_float(beta_posterior_probability),
                    "prior_odds": round_float(prior_odds),
                    "posterior_odds": round_float(posterior_odds),
                }
            )
            calculation_log.extend(evidence_log)
            warnings.append("在 Beta-binomial 更新之后又追加了证据更新，请确认这些证据没有被重复包含在已观测计数中。")
    elif method == "odds-update":
        prior_probability = float(prior_payload["probability"])
        posterior_probability, calculation_log, prior_odds, posterior_odds = apply_odds_update(prior_probability, evidence)
        posterior_interval = None
        posterior_block = {
            "prior_odds": prior_odds,
            "posterior_odds": posterior_odds,
            "posterior_probability": posterior_probability,
        }
    else:
        raise ValueError(f"Unsupported method: {method}")

    if any(item.get("quality") in {"D", "E"} for item in evidence):
        warnings.append("部分证据较弱或较间接，后验判断应视为更脆弱。")
    if any(float(item.get("dependency_discount", 1.0)) < 1.0 for item in evidence):
        warnings.append("至少有一条证据因依赖关系被折扣处理，不应把这次更新理解为完全独立证据的简单叠加。")
    if request.get("high_risk_domain"):
        warnings.append("本报告仅用于辅助决策，不替代持证专业人士的正式判断。")

    sensitivity = build_sensitivity(method, prior_payload, evidence, actions, observations, request.get("sensitivity") or {})
    if posterior_interval is None:
        posterior_interval = sensitivity["posterior_range"]
        warnings.append("这里的后验区间来自赔率更新下的敏感性包络，并非严格统计意义上的可信区间。")

    evaluated_actions = evaluate_actions(actions, posterior_probability) if actions else []
    recommendation = evaluated_actions[0]["name"] if evaluated_actions else "先继续收集信息"
    next_info = information_value_hint(
        evaluated_actions,
        posterior_probability,
        localize_list((request.get("next_information") or {}).get("candidates", []), "zh"),
    )
    confidence_code = recommendation_confidence(warnings, sensitivity["conclusion_stability_code"], evidence)
    confidence = confidence_label_zh(confidence_code)

    summary_sentence = (
        f"当前后验概率约为 {posterior_probability:.1%}；在现有证据下，更优的行动是 {recommendation}。"
    )

    return {
        "title": localize_text(request["title"], "zh"),
        "method": method,
        "summary": {
            "posterior_probability": round_float(posterior_probability),
            "credible_interval": [round_float(value) for value in posterior_interval] if posterior_interval else None,
            "recommendation": recommendation,
            "confidence": confidence,
            "confidence_code": confidence_code,
            "one_sentence": summary_sentence,
        },
        "question": {
            "decision_question": localize_text(request.get("question"), "zh"),
            "hypothesis": localize_text(request.get("hypothesis"), "zh"),
            "time_horizon": localize_text(request.get("time_horizon"), "zh"),
            "decision_deadline": localize_text(request.get("decision_deadline"), "zh"),
            "success_metric": localize_text(request.get("success_metric"), "zh"),
            "domain": localize_text(request.get("domain"), "zh"),
            "high_risk_domain": request.get("high_risk_domain", False),
        },
        "prior": {
            "probability": round_float(prior_payload["probability"]),
            "distribution": (
                f"Beta({round_float(prior_payload['alpha'])}, {round_float(prior_payload['beta'])})"
                if prior_payload.get("alpha") is not None and prior_payload.get("beta") is not None
                else "point prior"
            ),
            "source_summary": prior_payload.get("source_summary", []),
            "source_quality": localize_text(prior_payload.get("source_quality"), "zh"),
            "confidence": localize_text(prior_payload.get("confidence"), "zh"),
            "equivalent_sample_size": round_float(prior_payload.get("equivalent_sample_size")),
            "credible_interval": [round_float(value) for value in prior_payload.get("credible_interval", [])] or None,
        },
        "evidence": [
            {
                "name": item.get("name"),
                "summary": item.get("summary"),
                "quality": item.get("quality"),
                "direction": direction_label_zh(item.get("direction", "support")),
                "direction_code": item.get("direction", "support"),
                "likelihood_ratio": round_float(float(item.get("likelihood_ratio", 1.0))),
                "dependency_discount": round_float(float(item.get("dependency_discount", 1.0))),
                "notes": item.get("notes"),
            }
            for item in evidence
        ],
        "posterior": {
            "probability": round_float(posterior_probability),
            "credible_interval": [round_float(value) for value in posterior_interval] if posterior_interval else None,
            "method": method,
            "details": {key: normalize_value(value) for key, value in posterior_block.items()},
        },
        "decision": {
            "recommended_action": recommendation,
            "expected_value_ranking": evaluated_actions,
            "reason": (
                "当前基于后验概率的期望值比较，支持把这个行动作为首选。"
                if evaluated_actions
                else "没有提供行动效用参数，因此报告无法直接比较行动优先级。"
            ),
        },
        "sensitivity": sensitivity,
        "natural_frequency": natural_frequency(prior_payload["probability"], posterior_probability),
        "next_information": next_info,
        "warnings": warnings,
        "calculation_log": calculation_log,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Bayesian decision-report payload from a structured request.")
    parser.add_argument("input_json", help="Path to the structured decision request JSON file.")
    parser.add_argument("--output-json", help="Optional output path. Defaults to stdout when omitted.")
    args = parser.parse_args()

    try:
        request = load_request(Path(args.input_json))
        report = build_report(request)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(2) from exc

    if args.output_json:
        save_output(Path(args.output_json), report)
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
