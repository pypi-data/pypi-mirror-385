"""
Enhanced educational content generation tools.

This package contains tool wrappers that provide enhanced educational content
generation capabilities for the edu_agents tool infrastructure.

Note: Individual tool functions are imported directly in generator_agent.py
to avoid dependency issues when coach-bot dependencies are not available.
"""

# Note: No module-level imports to avoid triggering coach-bot dependency
# imports when the package is loaded. Individual modules are imported
# conditionally in generator_agent.py when needed.

__all__ = [
    "generate_coach_bot_clock_image_tool",
    "generate_coach_bot_angles_on_circle_image_tool", 
    "generate_coach_bot_single_angle_image_tool",
    "generate_coach_bot_multiple_angles_image_tool",
    "generate_coach_bot_fractional_angle_image_tool",
    "generate_coach_bot_area_model_image_tool",
    "generate_coach_bot_unit_square_decomposition_image_tool",
    "generate_coach_bot_single_bar_model_image_tool",
    "generate_coach_bot_comparison_bar_models_image_tool",
    "generate_coach_bot_base_ten_blocks_image_tool",
    "generate_coach_bot_base_ten_blocks_grid_image_tool",
    "generate_coach_bot_box_plots_image_tool",
    "generate_coach_bot_categorical_graph_image_tool",
    "generate_coach_bot_multi_bar_graph_image_tool",
    "generate_coach_bot_multi_picture_graph_image_tool",
    "generate_coach_bot_combo_points_table_graph_image_tool",
    "generate_coach_bot_counting_image_tool",
    "generate_coach_bot_data_table_with_graph_image_tool",
    "generate_coach_bot_decimal_grid_image_tool",
    "generate_coach_bot_decimal_comparison_image_tool",
    "generate_coach_bot_decimal_multiplication_image_tool",
    "generate_coach_bot_divide_into_equal_groups_image_tool",
    "generate_coach_bot_divide_items_into_array_image_tool",
    "generate_coach_bot_equation_tape_diagram_image_tool",
    "generate_coach_bot_flowchart_image_tool",
    "generate_coach_bot_fraction_models_image_tool",
    "generate_coach_bot_fraction_pairs_image_tool",
    "generate_coach_bot_fraction_multiplication_units_image_tool",
    "generate_coach_bot_divided_shapes_image_tool",
    "generate_coach_bot_unequal_fractions_image_tool",
    "generate_coach_bot_mixed_fractions_image_tool",
    "generate_coach_bot_whole_fractions_image_tool",
    "generate_coach_bot_fraction_strips_image_tool",
    "generate_coach_bot_3d_objects_image_tool",
    "generate_coach_bot_cross_section_image_tool",
    "generate_coach_bot_right_prisms_image_tool",
    "generate_coach_bot_geometric_shapes_image_tool",
    "generate_coach_bot_shapes_with_angles_image_tool",
    "generate_coach_bot_shape_with_right_angles_image_tool",
    "generate_coach_bot_linear_function_image_tool",
    "generate_coach_bot_quadratic_function_image_tool",
    "generate_coach_bot_exponential_function_image_tool",
    "generate_coach_bot_cubic_function_image_tool",
    "generate_coach_bot_square_root_function_image_tool",
    "generate_coach_bot_rational_function_image_tool",
    "generate_coach_bot_circle_function_image_tool",
    "generate_coach_bot_sideways_parabola_function_image_tool",
    "generate_coach_bot_hyperbola_function_image_tool",
    "generate_coach_bot_ellipse_function_image_tool",
    "generate_coach_bot_linear_function_quadrant_one_image_tool",
    "generate_coach_bot_quadratic_function_quadrant_one_image_tool",
    "generate_coach_bot_exponential_function_quadrant_one_image_tool",
    "generate_coach_bot_cubic_function_quadrant_one_image_tool",
    "generate_coach_bot_square_root_function_quadrant_one_image_tool",
    "generate_coach_bot_rational_function_quadrant_one_image_tool",
    # Piecewise function tools
    "generate_coach_bot_piecewise_function_image_tool",
    # Histogram tools
    "generate_coach_bot_histogram_image_tool",
    "generate_coach_bot_histogram_pair_image_tool",
    "generate_coach_bot_histogram_with_dotted_bin_image_tool",
    # Line plot tools
    "generate_coach_bot_single_line_plot_image_tool",
    "generate_coach_bot_stacked_line_plots_image_tool",
    "generate_coach_bot_double_line_plot_image_tool",
    # Lines of best fit tools
    "generate_coach_bot_lines_of_best_fit_image_tool",
    # Coordinate graphing tools
    "generate_coach_bot_coordinate_points_image_tool",
    "generate_coach_bot_coordinate_points_with_context_image_tool",
    "generate_coach_bot_scatter_plot_image_tool",
    "generate_coach_bot_stats_scatter_plot_image_tool",
    # Line graph tools  
    "generate_coach_bot_line_graph_image_tool",
    # Measurement tools
    "generate_coach_bot_measurement_comparison_image_tool",
    "generate_coach_bot_measurement_image_tool",
    # Number line tools
    "generate_coach_bot_number_line_clock_image_tool",
    "generate_coach_bot_number_line_image_tool",
    "generate_coach_bot_fixed_step_number_line_image_tool",
    "generate_coach_bot_unit_fraction_number_line_image_tool",
    "generate_coach_bot_extended_unit_fraction_number_line_image_tool",
    "generate_coach_bot_decimal_comparison_number_line_image_tool",
    "generate_coach_bot_vertical_number_line_image_tool",
    # Object array tools
    "generate_coach_bot_object_array_image_tool",
    # Protractor tools
    "generate_coach_bot_protractor_image_tool",
    # Polygon scale tools
    "generate_coach_bot_polygon_scale_image_tool",
    # Pedigree chart tools
    "generate_coach_bot_pedigree_chart_image_tool",
    # Prism net tools
    "generate_coach_bot_rectangular_prism_net_image_tool",
    "generate_coach_bot_cube_net_image_tool",
    "generate_coach_bot_triangular_prism_net_image_tool",
    "generate_coach_bot_square_pyramid_net_image_tool",
    "generate_coach_bot_rectangular_pyramid_net_image_tool",
    "generate_coach_bot_dual_prism_nets_image_tool",
    # Ratio object array tools
    "generate_coach_bot_ratio_object_array_image_tool",
    # Rectangular prisms tools
    "generate_coach_bot_rectangular_prisms_image_tool",
    "generate_coach_bot_base_area_prisms_image_tool",
    "generate_coach_bot_unit_cube_figure_image_tool",
    # Ruler measurement tools
    "generate_coach_bot_ruler_measurement_image_tool",
    # Shape decomposition tools
    "generate_coach_bot_shape_decomposition_image_tool",
    "generate_coach_bot_compound_area_figure_image_tool",
    "generate_coach_bot_rhombus_diagonals_image_tool",
    # Spinner tools
    "generate_coach_bot_spinner_image_tool",
    # Stepwise pattern tools
    "generate_coach_bot_stepwise_pattern_image_tool",
    # Symmetry tools
    "generate_coach_bot_lines_of_symmetry_image_tool",
    "generate_coach_bot_symmetry_identification_image_tool",
    # Table and scatterplots tools
    "generate_coach_bot_table_and_scatterplots_image_tool",
    # Table tools
    "generate_coach_bot_simple_table_image_tool",
    "generate_coach_bot_two_way_table_image_tool",
    "generate_coach_bot_probability_table_image_tool",
    "generate_coach_bot_data_table_image_tool",
    "generate_coach_bot_table_group_image_tool",
]