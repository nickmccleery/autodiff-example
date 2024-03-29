import auto_diff
import numpy as np
import pandas as pd


def compute_area_moment_of_inertia(
    depth: float,
    width: float,
    t_web: float,
    t_flange: float,
) -> float:
    """
    Compute the area moment of inertia of an I-beam cross-section.

    Ref: https://www.engineeringtoolbox.com/area-moment-inertia-d_1328.html

    Args:
        depth (float): The depth of the section.
        width (float): The width of the section.
        t_web (float): The thickness of the section's web.
        t_flange (float): The thickness of the section's flange.

    Returns:
        float: The area moment of inertia of the beam cross-section.
    """
    depth_web = depth - 2 * t_flange
    moi_x = (t_web * depth_web**3 / 12) + (width / 12) * (depth**3 - depth_web**3)

    return moi_x


def compute_area_moment_of_inertia_ad(x: np.ndarray) -> np.ndarray:
    """
    Wraps the compute_area_moment_of_inertia function to accept an array of inputs.

    Args:
        x (np.ndarray): An array of inputs containing the dimensions of the object.

    Returns:
        np.ndarray: The computed area moment of inertia.
    """
    return compute_area_moment_of_inertia(x[0], x[1], x[2], x[3])


def compute_area_moment_of_inertia_sensitivities(
    depth: float,
    width: float,
    t_web: float,
    t_flange: float,
):
    """
    Compute the area moment of inertia and sensitivities for a given set of parameters.

    Args:
        depth (float): The depth of the section.
        width (float): The width of the section.
        t_web (float): The thickness of the section's web.
        t_flange (float): The thickness of the section's flange.

    Returns:
        tuple: A tuple containing the area moment of inertia and sensitivities.
               The area moment of inertia is a scalar value.
               The sensitivities are a list of derivatives with respect to the input parameters.
    """
    x = np.array([[depth], [width], [t_web], [t_flange]])

    with auto_diff.AutoDiff(x) as x:
        moi_x = compute_area_moment_of_inertia_ad(x)

    moi = moi_x.val[0]

    # We only have one output, so the list of lists of lists can be flattened to a simple list.
    sensitivities_raw = moi_x.der.tolist()
    sensitivities = [x[0] for x in sensitivities_raw[0]]

    return (moi, sensitivities)


def run_gradient_ascent():
    """
    Run a simple projected gradient ascent algorithm to maximize the area moment of inertia, with projection to ensure
    parameters remain within specified bounds.
    """
    # Initial parameters.
    DEPTH_INIT = 100
    WIDTH_INIT = 50
    T_WEB = 5
    T_FLANGE = 5

    # Bound parameters.
    DEPTH_MIN = 100
    DEPTH_MAX = 200
    WIDTH_MIN = 50
    WIDTH_MAX = 100

    # Learning rate and number of iterations.
    learning_rate = 0.0001
    n_max_iterations = 100

    # Parameter vector
    x = np.array([[DEPTH_INIT], [WIDTH_INIT], [T_WEB], [T_FLANGE]])

    # Bounds for each parameter. [min, max] for each.
    bounds = np.array(
        [
            [DEPTH_MIN, DEPTH_MAX],
            [WIDTH_MIN, WIDTH_MAX],
            [T_WEB, T_WEB],
            [T_FLANGE, T_FLANGE],
        ]
    )

    # Set up the export parameters.
    out_iteration = []
    out_depth = []
    out_width = []
    out_moi = []

    for i in range(n_max_iterations):
        with auto_diff.AutoDiff(x) as xad:
            moi_x = compute_area_moment_of_inertia_ad(xad)

        moi = moi_x.val[0]
        depth = xad.val[0][0]
        width = xad.val[1][0]

        out_iteration.append(i)
        out_depth.append(depth)
        out_width.append(width)
        out_moi.append(moi)

        # Gradient ascent step.
        sensitivities = moi_x.der.tolist()
        x = np.array(xad.val) + learning_rate * np.array(sensitivities)
        x = x[0]

        # Projection step to ensure parameters remain within bounds.
        x = np.clip(x, bounds[:, 0].reshape(-1, 1), bounds[:, 1].reshape(-1, 1))

        # Check for convergence.
        if np.allclose(x, xad.val):
            break

    df = pd.DataFrame(
        {
            "iteration": out_iteration,
            "depth": out_depth,
            "width": out_width,
            "moi": out_moi,
        }
    )

    df.to_csv("solver_output.csv", index=False)


def sweep_depths():
    """
    Sweep a range of depths and compute the area moment of inertia and sensitivities for each depth.
    """
    depths = np.arange(100, 201, 10)
    width = 40
    t_web = 5
    t_flange = 5

    moi_out = []
    sensitivities_out = []

    for depth in depths:
        moi, sensitivities = compute_area_moment_of_inertia_sensitivities(
            depth, width, t_web, t_flange
        )
        moi_out.append(moi)
        sensitivities_out.append(sensitivities)

    df = pd.DataFrame(
        {
            "depth": depths,
            "i_xx": moi_out,
            "sens_depth": [s[0] for s in sensitivities_out],
            "sens_width": [s[1] for s in sensitivities_out],
            "sens_t_web": [s[2] for s in sensitivities_out],
            "sens_t_flange": [s[3] for s in sensitivities_out],
        }
    )

    df.to_csv("output.csv", index=False)


if __name__ == "__main__":
    run_gradient_ascent()
