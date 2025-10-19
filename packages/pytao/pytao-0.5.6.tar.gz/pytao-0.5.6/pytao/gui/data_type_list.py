data_type_list = []
data_type_list.append({"name": "", "data_source": ["beam", "lat"], "s_offset": True})
data_type_list.append(
    {
        "name": "alpha.<enum>",
        "<enum>": ["a", "b", "z"],
        "data_source": ["lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "apparent_emit.<enum>",
        "<enum>": ["x", "y"],
        "data_source": ["beam", "lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "norm_apparent_emit.<enum>",
        "<enum>": ["x", "y"],
        "data_source": ["beam", "lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "beta.<enum>",
        "<enum>": ["x", "y", "z", "a", "b", "c"],
        "data_source": ["beam", "lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "bpm_orbit.<enum>",
        "<enum>": ["x", "y"],
        "data_source": ["lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "bpm_eta.<enum>",
        "<enum>": ["x", "y"],
        "data_source": ["lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "bpm_phase.<enum>",
        "<enum>": ["a", "b"],
        "data_source": ["lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "bpm_k.<enum>",
        "<enum>": ["22a", "12a", "11b", "12b"],
        "data_source": ["lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "bpm_cbar.<enum>",
        "<enum>": ["22a", "12a", "11b", "12b"],
        "data_source": ["lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "bunch_min.<enum>",
        "<enum>": ["x", "px", "y", "py", "z", "pz"],
        "data_source": ["beam"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "bunch_max.<enum>",
        "<enum>": ["x", "px", "y", "py", "z", "pz"],
        "data_source": ["beam"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "bunch_charge.<enum>",
        "<enum>": ["live", "live_relative"],
        "data_source": ["beam"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "c_mat.<enum>",
        "<enum>": ["11", "12", "21", "22"],
        "data_source": ["lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "cbar.<enum>",
        "<enum>": ["11", "12", "21", "22"],
        "data_source": ["lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "chrom.<enum>",
        "<enum>": [
            "dtune.a",
            "a",
            "dtune.b",
            "b",
            "dbeta.a",
            "dbeta.b",
            "dphi.a",
            "dphi.b",
            "deta.x",
            "deta.y",
            "detap.x",
            "detap.y",
        ],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "damp.<enum>",
        "<enum>": ["j_a", "j_b", "j_z"],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append({"name": "dpx_dx", "data_source": ["beam"], "s_offset": False})
data_type_list.append({"name": "dpy_dy", "data_source": ["beam"], "s_offset": False})
data_type_list.append({"name": "dpz_dz", "data_source": ["beam"], "s_offset": False})
data_type_list.append({"name": "e_tot", "data_source": ["lat"], "s_offset": False})
data_type_list.append({"name": "e_tot_ref", "data_source": ["lat"], "s_offset": False})
data_type_list.append(
    {"name": "element_attrib.<str>", "data_source": ["lat"], "s_offset": False}
)
data_type_list.append(
    {
        "name": "emit.<enum>",
        "<enum>": ["x", "y", "z", "a", "b", "c"],
        "data_source": ["beam", "lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "norm_emit.<enum>",
        "<enum>": ["x", "y", "z", "a", "b", "c"],
        "data_source": ["beam", "lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "eta.<enum>",
        "<enum>": ["a", "b", "x", "y", "z"],
        "data_source": ["beam", "lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "etap.<enum>",
        "<enum>": ["a", "b", "x", "y"],
        "data_source": ["beam", "lat"],
        "s_offset": True,
    }
)
data_type_list.append({"name": "expression.<str>", "data_source": ["lat"], "s_offset": False})
data_type_list.append(
    {
        "name": "floor.<enum>",
        "<enum>": ["x", "y", "z", "theta", "phi", "psi"],
        "data_source": ["lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "floor_actual.<enum>",
        "<enum>": ["x", "y", "z", "theta", "phi", "psi"],
        "data_source": ["lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "floor_orbit.<enum>",
        "<enum>": ["x", "y", "z"],
        "data_source": ["beam", "lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "gamma.<enum>",
        "<enum>": ["a", "b", "z"],
        "data_source": ["lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "k.<enum>",
        "<enum>": ["11b", "12a", "12b", "22a"],
        "data_source": ["lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "srdt.<enum1>.<enum2>",
        "<enum1>": [
            "h20001",
            "h00201",
            "h10002",
            "h21000",
            "h30000",
            "h10110",
            "h10020",
            "h10200",
            "h31000",
            "h40000",
            "h20110",
            "h11200",
            "h20020",
            "h20200",
            "h00310",
            "h00400",
            "h22000",
            "h00220",
            "h11110",
        ],
        "<enum2>": ["r", "i", "a"],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "normal.h.<enum1>.<enum2>",
        "<enum1>": [
            "20001",
            "00201",
            "10002",
            "21000",
            "30000",
            "10110",
            "10020",
            "10200",
            "31000",
            "40000",
            "20110",
            "11200",
            "20020",
            "20200",
            "00310",
            "00400",
            "22000",
            "00220",
            "11110",
        ],
        "<enum2>": ["r", "i", "a"],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "normal.<enum>.<digit:1-6>.<digits6>",
        "<enum>": ["M", "A", "A_inv", "dhdj", "RaF", "ImF"],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append({"name": "momentum", "data_source": ["lat"], "s_offset": True})
data_type_list.append(
    {"name": "momentum_compaction", "data_source": ["lat"], "s_offset": False}
)
data_type_list.append({"name": "n_particle_loss", "data_source": ["beam"], "s_offset": False})
data_type_list.append(
    {
        "name": "orbit.<enum>",
        "<enum>": [
            "e_tot",
            "x",
            "y",
            "z",
            "px",
            "py",
            "pz",
            "amp_a",
            "amp_b",
            "norm_amp_a",
            "norm_amp_b",
        ],
        "data_source": ["beam", "lat"],
        "s_offset": True,
    }
)
data_type_list.append({"name": "pc", "data_source": ["beam", "lat"], "s_offset": False})
data_type_list.append({"name": "periodic.tt.<int>", "data_source": ["lat"], "s_offset": False})
data_type_list.append(
    {
        "name": "phase.<enum>",
        "<enum>": ["a", "b"],
        "data_source": ["lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "phase_frac.<enum>",
        "<enum>": ["a", "b"],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append({"name": "phase_frac_diff", "data_source": ["lat"], "s_offset": False})
data_type_list.append(
    {
        "name": "photon.<enum>",
        "<enum>": ["intensity_x", "intensity_y", "intensity", "phase_x", "phase_y"],
        "data_source": ["beam", "lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "ping_a.<enum>",
        "<enum>": [
            "amp_x",
            "phase_x",
            "amp_y",
            "phase_y",
            "amp_sin_y",
            "amp_cos_y",
            "amp_sin_rel_y",
            "amp_cos_rel_y",
        ],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "ping_b.<enum>",
        "<enum>": [
            "amp_y",
            "phase_y",
            "amp_x",
            "phase_x",
            "amp_sin_x",
            "amp_cos_x",
            "amp_sin_rel_x",
            "amp_cos_rel_x",
        ],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {"name": "r.<digit:1-6><digit:1-6>", "data_source": ["lat"], "s_offset": False}
)
data_type_list.append({"name": "r56_compaction", "data_source": ["lat"], "s_offset": False})
data_type_list.append(
    {
        "name": "rad_int.<enum>",
        "<enum>": [
            "i0",
            "i1",
            "i2",
            "i2_e4",
            "i3",
            "i3_e7",
            "i4a",
            "i4b",
            "i4z",
            "i5a",
            "i5a_e6",
            "i5b",
            "i5b_e6",
            "i6b",
        ],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "rad_int1.<enum>",
        "<enum>": [
            "i0",
            "i1",
            "i2",
            "i2_e4",
            "i3",
            "i3_e7",
            "i4a",
            "i5a",
            "i5a_e6",
            "i4b",
            "i5b",
            "i5b_e6",
            "i6b",
        ],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append({"name": "ref_time", "data_source": ["beam", "lat"], "s_offset": True})
data_type_list.append(
    {
        "name": "rel_floor.<enum>",
        "<enum>": ["x", "y", "z", "theta", "phi", "psi"],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "sigma.<enum>",
        "<enum>": ["x", "px", "y", "py", "z", "pz", "xy", "Lxy"],
        "data_source": ["beam", "lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "spin.<enum>",
        "<enum>": ["x", "y", "z", "amp"],
        "data_source": ["beam", "lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {"name": "spin.depolarization_rate", "data_source": ["lat"], "s_offset": False}
)
data_type_list.append(
    {"name": "spin.polarization_rate", "data_source": ["lat"], "s_offset": False}
)
data_type_list.append(
    {"name": "spin.polarization_limit", "data_source": ["lat"], "s_offset": False}
)
data_type_list.append(
    {
        "name": "spin_g_matrix.<enum>",
        "<enum>": [
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "21",
            "22",
            "23",
            "24",
            "25",
            "26",
        ],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append({"name": "s_position", "data_source": ["lat"], "s_offset": True})
data_type_list.append({"name": "time", "data_source": ["beam", "lat"], "s_offset": True})
data_type_list.append(
    {
        "name": "tune.<enum>",
        "<enum>": ["a", "b"],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append({"name": "t.<int>", "data_source": ["lat"], "s_offset": False})
data_type_list.append({"name": "tt.<int>", "data_source": ["lat"], "s_offset": False})
data_type_list.append(
    {
        "name": "unstable.<enum>",
        "<enum>": ["orbit", "ring"],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append(
    {
        "name": "velocity.<enum>",
        "<enum>": ["", "x", "y", "z"],
        "data_source": ["beam", "lat"],
        "s_offset": True,
    }
)
data_type_list.append(
    {
        "name": "wall.<enum>",
        "<enum>": ["left_side", "right_side"],
        "data_source": ["lat"],
        "s_offset": False,
    }
)
data_type_list.append({"name": "wire.<real>", "data_source": ["beam"], "s_offset": False})
