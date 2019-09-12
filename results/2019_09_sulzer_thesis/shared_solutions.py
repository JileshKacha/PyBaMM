#
# Simulations
#
import pybamm
import numpy as np


def model_comparison(models, Crates, t_eval, extra_parameter_values=None):
    " Solve models at a range of Crates "
    # load parameter values and geometry
    geometry = models[0].default_geometry
    extra_parameter_values = extra_parameter_values or {}
    param = models[0].default_parameter_values
    param.update(extra_parameter_values)

    # Process parameters (same parameters for all models)
    for model in models:
        param.process_model(model)
    param.process_geometry(geometry)

    # set mesh
    var = pybamm.standard_spatial_vars
    var_pts = {var.x_n: 10, var.x_s: 10, var.x_p: 10}
    mesh = pybamm.Mesh(geometry, models[-1].default_submesh_types, var_pts)

    # discretise models
    discs = {}
    for model in models:
        disc = pybamm.Discretisation(mesh, model.default_spatial_methods)
        disc.process_model(model)
        # Store discretisation
        discs[model] = disc

    # solve model for range of Crates
    all_variables = {}
    for Crate in Crates:
        all_variables[Crate] = {}
        current = Crate * 17
        pybamm.logger.info("Setting typical current to {} A".format(current))
        param.update({"Typical current [A]": current})
        for model in models:
            param.update_model(model, discs[model])
            solution = model.default_solver.solve(model, t_eval)
            variables = pybamm.post_process_variables(
                model.variables, solution.t, solution.y, mesh
            )
            variables["solution"] = solution
            all_variables[Crate][model.name] = variables

    return all_variables, t_eval


def error_comparison(models, Crates, t_eval, extra_parameter_values=None):
    " Solve models at differen Crates and sigmas and record the voltage "
    model_voltages = {model.name: {Crate: {} for Crate in Crates} for model in models}
    # load parameter values
    param = models[0].default_parameter_values
    # Update parameters
    extra_parameter_values = extra_parameter_values or {}
    param.update(extra_parameter_values)

    # set mesh
    var = pybamm.standard_spatial_vars

    # solve model for range of Crates and npts
    var_pts = {var.x_n: 20, var.x_s: 20, var.x_p: 20}

    # discretise models, store discretisation
    discs = {}
    for model in models:
        # Keep only voltage
        model.variables = {
            "Battery voltage [V]": model.variables["Battery voltage [V]"]
        }
        # Remove voltage cut off
        model.events = {
            name: event
            for name, event in model.events.items()
            if name != "Minimum voltage"
        }
        param.process_model(model)
        geometry = model.default_geometry
        param.process_geometry(geometry)
        mesh = pybamm.Mesh(geometry, model.default_submesh_types, var_pts)
        disc = pybamm.Discretisation(mesh, model.default_spatial_methods)
        disc.process_model(model)
        discs[model] = disc

    for Crate in Crates:
        current = Crate * 17
        pybamm.logger.info("""Setting typical current to {} A""".format(current))
        param.update({"Typical current [A]": current})
        for model in models:
            param.update_model(model, discs[model])
            try:
                solution = model.default_solver.solve(model, t_eval)
                success = True
            except pybamm.SolverError:
                pybamm.logger.error(
                    "Could not solve {!s} at {} A".format(model.name, current)
                )
                solution = "Could not solve {!s} at {} A".format(model.name, current)
                success = False
            if success:
                try:
                    voltage = pybamm.ProcessedVariable(
                        model.variables["Battery voltage [V]"],
                        solution.t,
                        solution.y,
                        mesh,
                    )(t_eval)
                except ValueError:
                    voltage = np.nan * np.ones_like(t_eval)
            else:
                voltage = np.nan * np.ones_like(t_eval)
            model_voltages[model.name][Crate] = voltage

    return model_voltages


def time_comparison(models, Crate, all_npts, t_eval, extra_parameter_values=None):
    " Solve models with different number of grid points and record the time taken"
    model_times = {model.name: {npts: {} for npts in all_npts} for model in models}
    # load parameter values
    param = models[0].default_parameter_values
    # Update parameters
    extra_parameter_values = extra_parameter_values or {}
    param.update({"Typical current [A]": Crate * 17, **extra_parameter_values})

    # set mesh
    var = pybamm.standard_spatial_vars

    # discretise models, store discretisation
    geometries = {}
    for model in models:
        # Remove all variables
        model.variables = {}
        # Remove voltage cut off
        model.events = {
            name: event
            for name, event in model.events.items()
            if name != "Minimum voltage"
        }
        param.process_model(model)
        geometry = model.default_geometry
        param.process_geometry(geometry)
        geometries[model] = geometry

    for npts in all_npts:
        pybamm.logger.info("Changing npts to {}".format(npts))
        for model in models:
            # solve model for range of Crates and npts
            var_pts = {var.x_n: npts, var.x_s: npts, var.x_p: npts}
            mesh = pybamm.Mesh(geometries[model], model.default_submesh_types, var_pts)
            disc = pybamm.Discretisation(mesh, model.default_spatial_methods)
            model_disc = disc.process_model(model, inplace=False)

            try:
                solution = model.default_solver.solve(model_disc, t_eval)
                time = solution.solve_time
            except pybamm.SolverError:
                pybamm.logger.error(
                    "Could not solve {!s} at {} A".format(model.name, Crate * 17)
                )
                time = np.nan
            model_times[model.name][npts] = time

    return model_times


def convergence_study(models, Crates, all_npts, t_eval, extra_parameter_values=None):
    " Solve models at a range of number of grid points "
    # load parameter values and geometry
    geometry = models[0].default_geometry
    param = models[0].default_parameter_values
    # Update parameters
    extra_parameter_values = extra_parameter_values or {}
    param.update(extra_parameter_values)

    # Process parameters (same parameters for all models)
    for model in models:
        param.process_model(model)
    param.process_geometry(geometry)

    # set mesh
    var = pybamm.standard_spatial_vars

    # solve model for range of Crates and npts
    models_times_and_voltages = {model.name: {} for model in models}
    for npts in all_npts:
        pybamm.logger.info("Setting number of grid points to {}".format(npts))
        var_pts = {var.x_n: npts, var.x_s: npts, var.x_p: npts}
        mesh = pybamm.Mesh(geometry, models[-1].default_submesh_types, var_pts)

        # discretise models, store discretised model and discretisation
        models_disc = {}
        discs = {}
        for model in models:
            disc = pybamm.Discretisation(mesh, model.default_spatial_methods)
            models_times_and_voltages[model.name][npts] = {}
            models_disc[model.name] = disc.process_model(model, inplace=False)
            discs[model.name] = disc

        # Solve for a range of C-rates
        for Crate in Crates:
            current = Crate * 17
            pybamm.logger.info("Setting typical current to {} A".format(current))
            param.update({"Typical current [A]": current})
            for model in models:
                model_disc = models_disc[model.name]
                disc = discs[model.name]
                param.update_model(model_disc, disc)
                try:
                    solution = model.default_solver.solve(model_disc, t_eval)
                except pybamm.SolverError:
                    pybamm.logger.error(
                        "Could not solve {!s} at {} A with {} points".format(
                            model.name, current, npts
                        )
                    )
                    continue
                voltage = pybamm.ProcessedVariable(
                    model_disc.variables["Battery voltage [V]"], solution.t, solution.y
                )(t_eval)
                variables = {
                    "Battery voltage [V]": voltage,
                    "solution object": solution,
                }
                models_times_and_voltages[model.name][npts][Crate] = variables

    return models_times_and_voltages


def simulation(models, t_eval, extra_parameter_values=None, disc_only=False):

    # create geometry
    geometry = models[-1].default_geometry

    # load parameter values and process models and geometry
    param = models[0].default_parameter_values
    extra_parameter_values = extra_parameter_values or {}
    param.update(extra_parameter_values)
    for model in models:
        param.process_model(model)
    param.process_geometry(geometry)

    # set mesh
    var = pybamm.standard_spatial_vars
    var_pts = {var.x_n: 25, var.x_s: 41, var.x_p: 34}
    mesh = pybamm.Mesh(geometry, models[-1].default_submesh_types, var_pts)

    # discretise models
    for model in models:
        disc = pybamm.Discretisation(mesh, model.default_spatial_methods)
        disc.process_model(model)

    if disc_only:
        return model, mesh

    # solve model
    solutions = [None] * len(models)
    for i, model in enumerate(models):
        solution = model.default_solver.solve(model, t_eval)
        solutions[i] = solution

    return models, mesh, solutions
