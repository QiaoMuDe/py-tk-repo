#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk

"""
插入子菜单
"""

def create_insert_submenu(parent_menu, root, menu_font_tuple):
    """
    创建插入子菜单，包含所有插入功能

    参数:
        parent_menu: 父菜单组件
        root: 主应用窗口实例
        menu_font_tuple: 菜单字体配置

    返回:
        配置好的插入子菜单
    """
    # 创建插入子菜单
    insert_submenu = tk.Menu(parent_menu, tearoff=0, font=menu_font_tuple)

    # 代码相关插入
    script_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="代码", menu=script_submenu)
    script_submenu.add_command(
        label="脚本 Shebang 行", command=lambda: root.insert_shebang()
    )
    script_submenu.add_command(
        label="Go语言基本结构", command=lambda: root.insert_go_basic()
    )
    script_submenu.add_command(
        label="GO函数模板", command=lambda: root.insert_go_function_template()
    )
    script_submenu.add_command(
        label="GO结构体模板", command=lambda: root.insert_go_struct_template()
    )
    script_submenu.add_command(
        label="Python编码声明", command=lambda: root.insert_encoding()
    )
    script_submenu.add_command(
        label="Python函数模板", command=lambda: root.insert_python_function_template()
    )
    script_submenu.add_command(
        label="Python类模板", command=lambda: root.insert_python_class_template()
    )
    script_submenu.add_command(
        label="HTML基本结构", command=lambda: root.insert_html_basic_structure()
    )
    script_submenu.add_command(
        label="CSS基本结构", command=lambda: root.insert_css_basic_structure()
    )
    script_submenu.add_command(
        label="JavaScript函数模板",
        command=lambda: root.insert_javascript_function_template(),
    )
    script_submenu.add_command(
        label="SQL查询模板", command=lambda: root.insert_sql_query_template()
    )

    # 文件相关插入
    file_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="文件", menu=file_submenu)
    file_submenu.add_command(label="文件名", command=lambda: root.insert_filename())
    file_submenu.add_command(label="文件路径", command=lambda: root.insert_filepath())
    file_submenu.add_command(label="目录路径", command=lambda: root.insert_directory())

    # 日期相关插入
    date_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="日期", menu=date_submenu)
    date_submenu.add_command(
        label="YYYY-MM-DD", command=lambda: root.insert_date("ymd")
    )
    date_submenu.add_command(
        label="YYYY/MM/DD", command=lambda: root.insert_date("ymd_slash")
    )
    date_submenu.add_command(
        label="DD-MM-YYYY", command=lambda: root.insert_date("dmy")
    )
    date_submenu.add_command(
        label="DD/MM/YYYY", command=lambda: root.insert_date("dmy_slash")
    )
    date_submenu.add_command(
        label="MM-DD-YYYY", command=lambda: root.insert_date("mdy")
    )
    date_submenu.add_command(
        label="MM/DD/YYYY", command=lambda: root.insert_date("mdy_slash")
    )

    # 时间相关插入
    time_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="时间", menu=time_submenu)
    time_submenu.add_command(
        label="24小时制 (HH:MM:SS)", command=lambda: root.insert_time("24h")
    )
    time_submenu.add_command(
        label="12小时制 (HH:MM:SS AM/PM)", command=lambda: root.insert_time("12h")
    )
    time_submenu.add_command(
        label="24小时制 (HH:MM)", command=lambda: root.insert_time("24h_short")
    )
    time_submenu.add_command(
        label="12小时制 (HH:MM AM/PM)", command=lambda: root.insert_time("12h_short")
    )

    # 日期时间相关插入
    datetime_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="日期时间", menu=datetime_submenu)
    datetime_submenu.add_command(
        label="YYYY-MM-DD HH:MM:SS", command=lambda: root.insert_datetime("ymd_24h")
    )
    datetime_submenu.add_command(
        label="YYYY-MM-DD HH:MM:SS AM/PM",
        command=lambda: root.insert_datetime("ymd_12h"),
    )
    datetime_submenu.add_command(
        label="YYYY/MM/DD HH:MM:SS",
        command=lambda: root.insert_datetime("ymd_slash_24h"),
    )
    datetime_submenu.add_command(
        label="YYYY/MM/DD HH:MM:SS AM/PM",
        command=lambda: root.insert_datetime("ymd_slash_12h"),
    )

    # 其他插入
    other_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="其他", menu=other_submenu)
    other_submenu.add_command(label="时间戳", command=lambda: root.insert_timestamp())

    # UUID子菜单
    uuid_submenu = tk.Menu(other_submenu, tearoff=0, font=menu_font_tuple)
    other_submenu.add_cascade(label="UUID", menu=uuid_submenu)
    uuid_submenu.add_command(
        label="UUID v4 (标准格式)", command=lambda: root.insert_uuid_v4()
    )
    uuid_submenu.add_command(
        label="无连字符UUID", command=lambda: root.insert_uuid_no_hyphens()
    )
    uuid_submenu.add_command(
        label="大写UUID", command=lambda: root.insert_uuid_uppercase()
    )
    uuid_submenu.add_command(
        label="大写无连字符UUID",
        command=lambda: root.insert_uuid_uppercase_no_hyphens(),
    )
    uuid_submenu.add_command(
        label="带花括号的UUID", command=lambda: root.insert_uuid_with_braces()
    )
    uuid_submenu.add_command(
        label="带花括号的大写UUID",
        command=lambda: root.insert_uuid_uppercase_with_braces(),
    )
    uuid_submenu.add_command(
        label="Base64编码UUID", command=lambda: root.insert_uuid_base64()
    )
    uuid_submenu.add_command(
        label="URN格式UUID", command=lambda: root.insert_uuid_urn()
    )
    uuid_submenu.add_command(
        label="UUID v1 (基于时间)", command=lambda: root.insert_uuid_v1()
    )

    # 特殊字符子菜单
    special_char_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="特殊字符", menu=special_char_submenu)

    # 常用特殊字符子菜单
    common_special_submenu = tk.Menu(
        special_char_submenu, tearoff=0, font=menu_font_tuple
    )
    special_char_submenu.add_cascade(label="常用特殊字符", menu=common_special_submenu)
    common_special_submenu.add_command(
        label="版权符号 ©", command=lambda: root.insert_copyright_symbol()
    )
    common_special_submenu.add_command(
        label="商标符号 ®", command=lambda: root.insert_trademark_symbol()
    )
    common_special_submenu.add_command(
        label="注册商标符号 ™",
        command=lambda: root.insert_registered_trademark_symbol(),
    )
    common_special_submenu.add_command(
        label="度数符号 °", command=lambda: root.insert_degree_symbol()
    )

    # 货币符号子菜单
    currency_submenu = tk.Menu(special_char_submenu, tearoff=0, font=menu_font_tuple)
    special_char_submenu.add_cascade(label="货币符号", menu=currency_submenu)
    currency_submenu.add_command(
        label="欧元符号 €", command=lambda: root.insert_euro_symbol()
    )
    currency_submenu.add_command(
        label="英镑符号 £", command=lambda: root.insert_pound_symbol()
    )
    currency_submenu.add_command(
        label="日元符号 ¥", command=lambda: root.insert_yen_symbol()
    )

    # 标点符号子菜单
    punctuation_submenu = tk.Menu(special_char_submenu, tearoff=0, font=menu_font_tuple)
    special_char_submenu.add_cascade(label="标点符号", menu=punctuation_submenu)
    punctuation_submenu.add_command(
        label="章节符号 §", command=lambda: root.insert_section_symbol()
    )
    punctuation_submenu.add_command(
        label="段落符号 ¶", command=lambda: root.insert_paragraph_symbol()
    )
    punctuation_submenu.add_command(
        label="省略号 …", command=lambda: root.insert_ellipsis_symbol()
    )
    punctuation_submenu.add_command(
        label="匕首符号 †", command=lambda: root.insert_dagger_symbol()
    )
    punctuation_submenu.add_command(
        label="双匕首符号 ‡", command=lambda: root.insert_double_dagger_symbol()
    )
    punctuation_submenu.add_command(
        label="圆点符号 •", command=lambda: root.insert_bullet_symbol()
    )

    # 数学符号子菜单
    math_symbol_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="数学符号", menu=math_symbol_submenu)

    # 常用数学符号子菜单
    common_math_submenu = tk.Menu(math_symbol_submenu, tearoff=0, font=menu_font_tuple)
    math_symbol_submenu.add_cascade(label="常用数学符号", menu=common_math_submenu)
    common_math_submenu.add_command(
        label="正负号 ±", command=lambda: root.insert_plus_minus_symbol()
    )
    common_math_submenu.add_command(
        label="不等号 ≠", command=lambda: root.insert_not_equal_symbol()
    )
    common_math_submenu.add_command(
        label="小于等于号 ≤", command=lambda: root.insert_less_than_or_equal_symbol()
    )
    common_math_submenu.add_command(
        label="大于等于号 ≥", command=lambda: root.insert_greater_than_or_equal_symbol()
    )
    common_math_submenu.add_command(
        label="无穷符号 ∞", command=lambda: root.insert_infinity_symbol()
    )

    # 微积分符号子菜单
    calculus_submenu = tk.Menu(math_symbol_submenu, tearoff=0, font=menu_font_tuple)
    math_symbol_submenu.add_cascade(label="微积分符号", menu=calculus_submenu)
    calculus_submenu.add_command(
        label="求和符号 ∑", command=lambda: root.insert_summation_symbol()
    )
    calculus_submenu.add_command(
        label="乘积符号 ∏", command=lambda: root.insert_product_symbol()
    )
    calculus_submenu.add_command(
        label="积分符号 ∫", command=lambda: root.insert_integral_symbol()
    )
    calculus_submenu.add_command(
        label="偏导数符号 ∂", command=lambda: root.insert_partial_derivative_symbol()
    )
    calculus_submenu.add_command(
        label="梯度符号 ∇", command=lambda: root.insert_nabla_symbol()
    )

    # 根号符号子菜单
    root_submenu = tk.Menu(math_symbol_submenu, tearoff=0, font=menu_font_tuple)
    math_symbol_submenu.add_cascade(label="根号符号", menu=root_submenu)
    root_submenu.add_command(
        label="平方根符号 √", command=lambda: root.insert_square_root_symbol()
    )
    root_submenu.add_command(
        label="立方根符号 ∛", command=lambda: root.insert_cubic_root_symbol()
    )
    root_submenu.add_command(
        label="四次根符号 ∜", command=lambda: root.insert_fourth_root_symbol()
    )

    # 希腊字母子菜单
    greek_submenu = tk.Menu(math_symbol_submenu, tearoff=0, font=menu_font_tuple)
    math_symbol_submenu.add_cascade(label="希腊字母", menu=greek_submenu)

    # 小写希腊字母子菜单
    greek_lower_submenu = tk.Menu(greek_submenu, tearoff=0, font=menu_font_tuple)
    greek_submenu.add_cascade(label="小写希腊字母", menu=greek_lower_submenu)
    greek_lower_submenu.add_command(
        label="α", command=lambda: root.insert_alpha_symbol()
    )
    greek_lower_submenu.add_command(
        label="β", command=lambda: root.insert_beta_symbol()
    )
    greek_lower_submenu.add_command(
        label="γ", command=lambda: root.insert_gamma_symbol()
    )
    greek_lower_submenu.add_command(
        label="δ", command=lambda: root.insert_delta_symbol()
    )
    greek_lower_submenu.add_command(
        label="ε", command=lambda: root.insert_epsilon_symbol()
    )
    greek_lower_submenu.add_command(
        label="ζ", command=lambda: root.insert_zeta_symbol()
    )
    greek_lower_submenu.add_command(label="η", command=lambda: root.insert_eta_symbol())
    greek_lower_submenu.add_command(
        label="θ", command=lambda: root.insert_theta_symbol()
    )
    greek_lower_submenu.add_command(
        label="ι", command=lambda: root.insert_iota_symbol()
    )
    greek_lower_submenu.add_command(
        label="κ", command=lambda: root.insert_kappa_symbol()
    )
    greek_lower_submenu.add_command(
        label="λ", command=lambda: root.insert_lambda_symbol()
    )
    greek_lower_submenu.add_command(label="μ", command=lambda: root.insert_mu_symbol())
    greek_lower_submenu.add_command(label="ν", command=lambda: root.insert_nu_symbol())
    greek_lower_submenu.add_command(label="ξ", command=lambda: root.insert_xi_symbol())
    greek_lower_submenu.add_command(
        label="ο", command=lambda: root.insert_omicron_symbol()
    )
    greek_lower_submenu.add_command(label="π", command=lambda: root.insert_pi_symbol())
    greek_lower_submenu.add_command(label="ρ", command=lambda: root.insert_rho_symbol())
    greek_lower_submenu.add_command(
        label="σ", command=lambda: root.insert_sigma_symbol()
    )
    greek_lower_submenu.add_command(label="τ", command=lambda: root.insert_tau_symbol())
    greek_lower_submenu.add_command(
        label="υ", command=lambda: root.insert_upsilon_symbol()
    )
    greek_lower_submenu.add_command(label="φ", command=lambda: root.insert_phi_symbol())
    greek_lower_submenu.add_command(label="χ", command=lambda: root.insert_chi_symbol())
    greek_lower_submenu.add_command(label="ψ", command=lambda: root.insert_psi_symbol())
    greek_lower_submenu.add_command(
        label="ω", command=lambda: root.insert_omega_symbol()
    )

    # 大写希腊字母子菜单
    greek_upper_submenu = tk.Menu(greek_submenu, tearoff=0, font=menu_font_tuple)
    greek_submenu.add_cascade(label="大写希腊字母", menu=greek_upper_submenu)
    greek_upper_submenu.add_command(
        label="Α", command=lambda: root.insert_capital_alpha_symbol()
    )
    greek_upper_submenu.add_command(
        label="Β", command=lambda: root.insert_capital_beta_symbol()
    )
    greek_upper_submenu.add_command(
        label="Γ", command=lambda: root.insert_capital_gamma_symbol()
    )
    greek_upper_submenu.add_command(
        label="Δ", command=lambda: root.insert_capital_delta_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ε", command=lambda: root.insert_capital_epsilon_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ζ", command=lambda: root.insert_capital_zeta_symbol()
    )
    greek_upper_submenu.add_command(
        label="Η", command=lambda: root.insert_capital_eta_symbol()
    )
    greek_upper_submenu.add_command(
        label="Θ", command=lambda: root.insert_capital_theta_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ι", command=lambda: root.insert_capital_iota_symbol()
    )
    greek_upper_submenu.add_command(
        label="Κ", command=lambda: root.insert_capital_kappa_symbol()
    )
    greek_upper_submenu.add_command(
        label="Λ", command=lambda: root.insert_capital_lambda_symbol()
    )
    greek_upper_submenu.add_command(
        label="Μ", command=lambda: root.insert_capital_mu_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ν", command=lambda: root.insert_capital_nu_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ξ", command=lambda: root.insert_capital_xi_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ο", command=lambda: root.insert_capital_omicron_symbol()
    )
    greek_upper_submenu.add_command(
        label="Π", command=lambda: root.insert_capital_pi_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ρ", command=lambda: root.insert_capital_rho_symbol()
    )
    greek_upper_submenu.add_command(
        label="Σ", command=lambda: root.insert_capital_sigma_symbol()
    )
    greek_upper_submenu.add_command(
        label="Τ", command=lambda: root.insert_capital_tau_symbol()
    )
    greek_upper_submenu.add_command(
        label="Υ", command=lambda: root.insert_capital_upsilon_symbol()
    )
    greek_upper_submenu.add_command(
        label="Φ", command=lambda: root.insert_capital_phi_symbol()
    )
    greek_upper_submenu.add_command(
        label="Χ", command=lambda: root.insert_capital_chi_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ψ", command=lambda: root.insert_capital_psi_symbol()
    )
    greek_upper_submenu.add_command(
        label="Ω", command=lambda: root.insert_capital_omega_symbol()
    )

    # 颜色代码子菜单
    color_code_submenu = tk.Menu(insert_submenu, tearoff=0, font=menu_font_tuple)
    insert_submenu.add_cascade(label="颜色代码", menu=color_code_submenu)
    color_code_submenu.add_command(
        label="HEX颜色代码选择器", command=lambda: root.insert_hex_color_picker()
    )
    color_code_submenu.add_command(
        label="RGB颜色代码选择器", command=lambda: root.insert_rgb_color_picker()
    )

    return insert_submenu