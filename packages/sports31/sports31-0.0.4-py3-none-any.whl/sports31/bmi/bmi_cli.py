from math import inf
import pandas as pd
import click

from sports31.bmi.bmi import bmi, toweight

hw = "上限体重(kg)"
bmirange = "BMI范围"
data = {
    "low": [0, 18.5, 25, 30, 35, 40],
    "high": [18.5, 25, 30, 35, 40, inf],
    hw: [18.5, 25, 30, 35, 40, inf],
    bmirange: [
        "BMI<=18.5",
        "18.5<BMI<=25",
        "25<BMI<=30",
        "30<BMI<=35",
        "35<BMI<=40",
        "40<BMI",
    ],
}
df = pd.DataFrame(
    data, index=["偏瘦", "正常", "超重", "轻度肥胖", "中度肥胖", "重度肥胖"]
)
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option("display.unicode.ambiguous_as_wide", True)


@click.command("bmi")
@click.option("--height", help="身高，单位cm。", type=click.FLOAT)
@click.option("--weight", help="体重，单位kg。", type=click.FLOAT)
def cli(height, weight):
    bmi_value = bmi(weight, height)
    click.echo(
        f"BMI指数: {bmi_value:.2f} （身高：{height:.0f}cm，体重：{weight:0.1f}kg）"
    )
    df[hw] = df[hw].apply(lambda x: format(toweight(x, height), ".1f"))
    click.echo(df.loc[:, [bmirange, hw]])


if __name__ == "__main__":
    cli()
