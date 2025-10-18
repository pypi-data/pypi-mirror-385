from mammoth_commons.datasets import CSV
from mammoth_commons.models.onnx_ensemble import ONNXEnsemble
from mammoth_commons.exports import HTML
from typing import Dict, List
from mammoth_commons.integration import metric, Options
import numpy as np
from mammoth_commons.externals import fb_categories


@metric(
    namespace="mammotheu",
    version="v0049",
    python="3.13",
    packages=(
        "fairbench",
        "plotly",
        "pandas",
        "onnxruntime",
        "ucimlrepo",
        "pygrank",
        "mmm-fair-cli",
        "skl2onnx",
    ),
)
def multi_objective_report(
    dataset: CSV,
    model: ONNXEnsemble,
    sensitive: List[str],
) -> HTML:
    """<img src="https://raw.githubusercontent.com/arjunroyihrpa/MMM_fair/main/images/mmm-fair.png" alt="Based on MMM-Fair" style="float: left; margin-right: 5px; margin-bottom: 5px; height: 80px;"/>

    <p>This module presents an interactive <a href="https://plotly.com/python/3d-charts/" target="_blank">Plotly 3D plot</a>
    visualizing multiple objectives to evaluate model fairness and performance trade-offs. The report highlights three
    primary objectives: <b>accuracy loss</b>, <b>balanced accuracy loss</b>, and <b>discrimination (MMM-fairness)
    loss</b>. Each point plotted within the 3D space represents a <i>Pareto-optimal</i> solution, which achieves an
    optimal balance between these objectives where no single objective can improve without worsening another.</p>

    <p>Users can hover over any solution point to display the corresponding loss values for each objective.
    Additionally, each point includes a <b>theta</b> value, indicating up to which sequence in the ONNX
    ensemble the particular solution is achieved. This allows users to observe performance changes throughout
    different stages of the ensemble, helping them better understand the trade-offs involved in each model
    configuration.</p>

    <span class="alert alert-warning alert-dismissible fade show" role="alert"
    style="display: inline-block; padding: 10px;"> <i class="bi bi-exclamation-triangle-fill"></i> The multi-objective
    report generates predictions at each step of the partial ensemble. This may result in slower processing
    times when the number of Pareto solutions is high.</span>
    """
    from fairbench import v1 as fb
    from mmm_fair_cli.viz_trade_offs import plot3d

    # obtain predictions
    if hasattr(model, "mmm"):
        model = model.mmm
    if hasattr(model, "pareto") and model.pareto is not None:
        thetas = model.pareto
    else:
        thetas = np.arange(2, len(model.models))
    O_1, O_2, O_3 = [], [], []
    labs = list(dataset.labels.__iter__())[-1]
    labs = labs.to_numpy() if hasattr(labs, "to_numpy") else np.array(labs)
    for i in thetas:
        predictions = model.predict(dataset, sensitive, theta=i)
        O_1.append(1 - float(fb.accuracy(predictions=predictions, labels=labs)))
        O_2.append(
            1
            - (
                float(fb.tpr(predictions=predictions, labels=labs))
                + float(fb.tnr(predictions=predictions, labels=labs))
            )
            / 2
        )
        mm_fair = []
        for attr in sensitive:
            prots = fb.Fork(fb_categories(dataset.df[attr]))
            groups = list(prots.branches().keys())  # [g for g in prots]#
            dfnr = fb.dfnr(predictions=predictions, labels=labs, sensitive=prots)
            dfpr = fb.dfpr(predictions=predictions, labels=labs, sensitive=prots)
            mm_fair.append(
                max(
                    [
                        max([float(dfnr[g]) for g in groups]),
                        max([float(dfpr[g]) for g in groups]),
                    ]
                )
            )
            # mm_fair.append(max([fb.areduce(dfpr, fb.max), fb.areduce(dfnr, fb.max)]))
        O_3.append(max(mm_fair))
        # print(O_1[-1], O_2[-1], O_3[-1])
        # obs.append([O_1,O_2,O_3

    plot_html = plot3d(x=O_1, y=O_2, z=O_3, html=True)

    html = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Multi-objective Report</title>
            <style>
            body {{
                margin: 0;
                padding: 20px;
                box-sizing: border-box;
                font-family: system-ui, sans-serif;
                background-color: #fafafa;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                text-align: center;
            }}
            .about {{
                margin-bottom: 20px;
                line-height: 1.5;
            }}
            </style>
        </head>
        <body>
            <div class="container">
            <h1>About</h1>
            <p class="about">
                The report highlights three primary objectives: accuracy loss, balanced accuracy loss, and discrimination (MMM-fairness) loss.
                Each point plotted within the 3D space represents a Pareto-optimal solution, which achieves an optimal balance between these
                objectives where no single objective can improve without worsening another.
            </p>
            <p class="about">
                Users can hover over any solution point to display the corresponding loss values for each objective. Additionally, each point
                includes a theta value, indicating up to which sequence in the ONNX ensemble the particular solution is achieved. This allows
                users to observe performance changes throughout different stages of the ensemble, helping them better understand the trade-offs
                involved in each model configuration.
            </p>
            {plot_html}
            </div>
        </body>
        </html>
        """
    return HTML(html)  # fb.interactive_html(report, show=False, name="Classes"))
