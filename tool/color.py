import pandas as pd
from plotly.colors import sample_colorscale


def assign_dynamic_colors(
    data,
    mode="relative_max",
    threshold=200,
):
    result = data.copy()

    result["customers"] = pd.to_numeric(
        result["customers"],
        errors="raise",
    )

    if result["customers"].isna().any():
        raise ValueError("customers 含有缺失值，請先處理。")

    if result.empty:
        result["marker_color"] = pd.Series(dtype="object")
        return result

    values = result["customers"]

    # 最大值模式：所有並列最大值都顯示紅色
    if mode == "relative_max":
        red_mask = values.eq(values.max())

    # 門檻模式：嚴格大於 threshold 才顯示紅色
    elif mode == "threshold":
        red_mask = values.gt(threshold)

    else:
        raise ValueError(
            "mode 必須是 'relative_max' 或 'threshold'"
        )

    result["marker_color"] = "#CBD2DA"

    # -------------------------
    # 非紅色資料：淺藍 → 深藍
    # -------------------------
    blue_mask = ~red_mask
    blue_values = values[blue_mask]

    if not blue_values.empty:
        blue_min = blue_values.min()
        blue_max = blue_values.max()

        if blue_max == blue_min:
            blue_positions = [0.5] * len(blue_values)
        else:
            blue_positions = (
                (blue_values - blue_min)
                / (blue_max - blue_min)
            ).tolist()

        result.loc[blue_mask, "marker_color"] = (
            sample_colorscale(
                [
                    [0.0, "#CBDDEA"],
                    [1.0, "#1976C9"],
                ],
                blue_positions,
            )
        )

    # -------------------------
    # 紅色資料
    # -------------------------
    if red_mask.any():
        if mode == "relative_max":
            result.loc[red_mask, "marker_color"] = "#B40D37"

        else:
            red_values = values[red_mask]

            # 以門檻為起點，目前最大值為終點
            red_positions = (
                (red_values - threshold)
                / (red_values.max() - threshold)
            ).tolist()

            result.loc[red_mask, "marker_color"] = (
                sample_colorscale(
                    [
                        [0.0, "#F48A91"],  # 接近門檻：淺紅
                        [1.0, "#B40D37"],  # 目前最大：深紅
                    ],
                    red_positions,
                )
            )

    return result
