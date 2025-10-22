   
from pyflange.logger import Logger, log_data
logger = Logger(__name__)

from pyflange.flangesegments import PolynomialTFlangeSegment, bolt_markov_matrix, shell_stiffness
from pyflange.bolts import MetricBolt, HexNut
from pyflange.gap import gap_height_distribution
from pyflange.fatigue import markov_matrix_from_SGRE_format, BoltFatigueCurve

from math import pi
import numpy as np

from workbook import open_workbook, flangesegment_to_excel


# Units of measurement
m = 1
mm = 0.001*m

kg = 1
t = 1000*kg

s = 1

N = kg*m/s**2
kN = 1000*N

Pa = 1
MPa = 1e6*Pa
GPa = 1e9*Pa

rad = 1
deg = (pi/180)*rad



# Bolt

M48 = MetricBolt(
    nominal_diameter = 48*mm,
    thread_pitch = 5*mm,
    shank_diameter_ratio = 44.752/48,
    shank_length = 150*mm,
    yield_stress = 900*MPa,
    ultimate_tensile_stress = 1000*MPa,
    stud = True)

M48_hex_nut = HexNut(
    nominal_diameter = 48*mm,
    thickness = 64*mm,
    inscribed_diameter = 75*mm,
    circumscribed_diameter = 82.6*mm,
    bearing_diameter = 92*mm
)

# Polinomial Segment Model
def create_flange_segment (gap_angle, gap_shape_factor=1.0, tilt_angle=0, macro_geometric_factor=1.0, k_shell_option=0):

    D = 7500*mm
    t_sh = 90*mm
    n = 200 # number of bolts
    gap_length = gap_angle * D/2
    gap = gap_height_distribution(D, 0.0014, gap_length)

    k_mean = gap.mean()
    COV_k = gap.std() / k_mean

    fseg = PolynomialTFlangeSegment(

        a = 62.5*mm,           # distance between inner face of the flange and center of the bolt hole
        b = 111.0*mm,           # distance between center of the bolt hole and center-line of the shell
        s = t_sh,               # shell thickness
        t = 120.0*mm,           # flange thickness
        R = D/2,                # shell outer curvature radius
        central_angle = 2*pi/n, # angle subtented by the flange segment arc

        Zg = -81.4*kN*macro_geometric_factor,     # load applied to the flange segment shell at rest
                                # (normally dead weight of tower + RNA, divided by the number of bolts)

        bolt = M48,
        Fv = 928*kN,       # applied bolt preload

        Do = 52*mm,         # bolt hole diameter
        washer = None,      # no washer
        nut = M48_hex_nut,  # bolt nut

        gap_height = gap.ppf(0.95),             # maximum longitudinal gap height
        gap_angle = gap_angle,                  # longitudinal gap length
        gap_shape_factor = gap_shape_factor,    # scaling factor accounting for the gap shape

        tilt_angle = tilt_angle,    # flange tilt angle

        s_ratio = 1.0,    # ratio of bottom shell thickness over tower shell thickness
        k_shell=calculate_k_shell(k_shell_option,gap_angle)
    )

    # Assert that failure mode is B.
    #fseg.validate(335*MPa, 285*MPa)

    log_data(fseg, k_mean=k_mean, COV_k=COV_k)

    return fseg    

def calculate_damage(fseg,macro_geometric_factor=1.0):
    markov_path="tflange-example-markov.mkv"
    df_markov_shell=markov_matrix_from_SGRE_format(markov_path)
    df_markov_bolt=bolt_markov_matrix(fseg,
                                      df_markov_shell,
                                      bending_factor=0.601,
                                      mean_factor=1.0*macro_geometric_factor,
                                      range_factor=1.19*macro_geometric_factor)
                                                      
    bfc=BoltFatigueCurve(M48.nominal_diameter)
    dmg=bfc.cumulated_damage(df_markov_bolt)
    return dmg

def calculate_k_shell(k_shell_option,gap_angle):
    if k_shell_option==0:
        return None
    elif k_shell_option==1:
        k_shell=shell_stiffness(7.5/2,0.09,gap_angle)
    else:
        if gap_angle==30*deg: k_shell=4970*1e6
        elif gap_angle==60*deg: k_shell=2088*1e6
        elif gap_angle==90*deg: k_shell=1100*1e6
        elif gap_angle==120*deg: k_shell=618*1e6
        else: k_shell=None
    return k_shell
    pass

Case_5_simplified=False
Case_6_simplified=False
Case_7_simplified=False
Case_8_simplified=False

Case_5_interpolated=True
Case_6_interpolated=True
Case_7_interpolated=True
Case_8_interpolated=True

#macro_geometric_factor
macro_geometric_factor=1.3

#### Simplified Shell Stiffness
k_shell_option=0

#### Case 5
if Case_5_simplified:
    print("\nEvaluating Flange Segment Model with sinusoidal gap shape and no flange tilt ...")
    wb = open_workbook("Case_5-D7500_Tilt-0deg_ShapeFactor-1.0.xlsx")
    
    print("... with 30 deg gap width")
    fseg_30deg  = create_flange_segment( 30*deg, macro_geometric_factor=macro_geometric_factor, k_shell_option=k_shell_option)
    dmg_30deg = calculate_damage(fseg_30deg, macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb, "Gap30deg", fseg_30deg, dmg_30deg)
    
    print("... with 60 deg gap width")
    fseg_60deg  = create_flange_segment( 60*deg, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_60deg = calculate_damage(fseg_60deg,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb, "Gap60deg", fseg_60deg, dmg_60deg)
    
    print("... with 90 deg gap width")
    fseg_90deg  = create_flange_segment( 90*deg, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_90deg = calculate_damage(fseg_90deg,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb, "Gap90deg", fseg_90deg, dmg_90deg)
    
    print("... with 120 deg gap width")
    fseg_120deg = create_flange_segment(120*deg, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_120deg = calculate_damage(fseg_120deg,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb, "Gap120deg", fseg_120deg, dmg_120deg)


#### Case 6
if Case_6_simplified:
    print("\nEvaluating Flange Segment Model with gap shape factor 1.5 and no flange tilt ...")
    wb_sf = open_workbook("Case_6-D7500_Tilt-0deg_ShapeFactor-1.5.xlsx")
    
    print("... with 30 deg gap width")
    fseg_30deg_sf  = create_flange_segment( 30*deg, 1.5, macro_geometric_factor=macro_geometric_factor)
    dmg_30deg_sf = calculate_damage(fseg_30deg_sf,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sf, "Gap30deg", fseg_30deg_sf, dmg_30deg_sf)
    
    print("... with 60 deg gap width")
    fseg_60deg_sf  = create_flange_segment( 60*deg, 1.5, macro_geometric_factor=macro_geometric_factor)
    dmg_60deg_sf = calculate_damage(fseg_60deg_sf,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sf, "Gap60deg", fseg_60deg_sf, dmg_60deg_sf)
    
    print("... with 90 deg gap width")
    fseg_90deg_sf  = create_flange_segment( 90*deg, 1.5, macro_geometric_factor=macro_geometric_factor)
    dmg_90deg_sf = calculate_damage(fseg_90deg_sf,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sf, "Gap90deg", fseg_90deg_sf,dmg_90deg_sf)
    
    print("... with 120 deg gap width")
    fseg_120deg_sf = create_flange_segment(120*deg, 1.5, macro_geometric_factor=macro_geometric_factor)
    dmg_120deg_sf = calculate_damage(fseg_120deg_sf,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sf, "Gap120deg", fseg_120deg_sf, dmg_120deg_sf)


#### Case 7
if Case_7_simplified:
    print("\nEvaluating Flange Segment Model with gap shape factor 1.5 and 1 deg flange tilt ...")
    wb_sftt = open_workbook("Case_7-D7500_Tilt-1deg_ShapeFactor-1.5.xlsx")
    
    print("... with 30 deg gap width")
    fseg_30deg_sftt  = create_flange_segment( 30*deg, 1.5, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor)
    dmg_30deg_sftt = calculate_damage(fseg_30deg_sftt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sftt, "Gap30deg", fseg_30deg_sftt, dmg_30deg_sftt)
    
    print("... with 60 deg gap width")
    fseg_60deg_sftt  = create_flange_segment( 60*deg, 1.5, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor)
    dmg_60deg_sftt = calculate_damage(fseg_60deg_sftt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sftt, "Gap60deg", fseg_60deg_sftt, dmg_60deg_sftt)
    
    print("... with 90 deg gap width")
    fseg_90deg_sftt  = create_flange_segment( 90*deg, 1.5, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor)
    dmg_90deg_sftt = calculate_damage(fseg_90deg_sftt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sftt, "Gap90deg", fseg_90deg_sftt, dmg_90deg_sftt)
    
    print("... with 120 deg gap width")
    fseg_120deg_sftt = create_flange_segment(120*deg, 1.5, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor)
    dmg_129deg_sftt = calculate_damage(fseg_120deg_sftt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sftt, "Gap120deg", fseg_120deg_sftt, dmg_129deg_sftt)


#### Case 8
if Case_8_simplified:
    print("\nEvaluating Flange Segment Model with sinusoidal gap shape and 1 deg flange tilt ...")
    wb_tt = open_workbook("Case_8-D7500_Tilt-1deg_ShapeFactor-1.0.xlsx")
    
    print("... with 30 deg gap width")
    fseg_30deg_tt  = create_flange_segment( 30*deg, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor)
    dmg_30deg_tt = calculate_damage(fseg_30deg_tt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_tt, "Gap30deg", fseg_30deg_tt, dmg_30deg_tt)
    
    print("... with 60 deg gap width")
    fseg_60deg_tt  = create_flange_segment( 60*deg, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor)
    dmg_60deg_tt = calculate_damage(fseg_60deg_tt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_tt, "Gap60deg", fseg_60deg_tt, dmg_60deg_tt)
    
    print("... with 90 deg gap width")
    fseg_90deg_tt  = create_flange_segment( 90*deg, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor)
    dmg_90deg_tt = calculate_damage(fseg_90deg_tt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_tt, "Gap90deg", fseg_90deg_tt, dmg_90deg_tt)
    
    print("... with 120 deg gap width")
    fseg_120deg_tt = create_flange_segment(120*deg, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor)
    dmg_129deg_tt = calculate_damage(fseg_120deg_tt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_tt, "Gap120deg", fseg_120deg_tt, dmg_129deg_tt)


#### Interpolated Shell Stiffness
k_shell_option=1

#### Case 5
if Case_5_interpolated:
    print("\nEvaluating Flange Segment Model with sinusoidal gap shape and no flange tilt ...")
    wb = open_workbook("Case_5-D7500_Tilt-0deg_ShapeFactor-1.0-interpolated.xlsx")
    
    print("... with 30 deg gap width")
    fseg_30deg  = create_flange_segment( 30*deg, macro_geometric_factor=macro_geometric_factor, k_shell_option=k_shell_option)
    dmg_30deg = calculate_damage(fseg_30deg, macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb, "Gap30deg", fseg_30deg, dmg_30deg)
    
    print("... with 60 deg gap width")
    fseg_60deg  = create_flange_segment( 60*deg, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_60deg = calculate_damage(fseg_60deg,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb, "Gap60deg", fseg_60deg, dmg_60deg)
    
    print("... with 90 deg gap width")
    fseg_90deg  = create_flange_segment( 90*deg, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_90deg = calculate_damage(fseg_90deg,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb, "Gap90deg", fseg_90deg, dmg_90deg)
    
    print("... with 120 deg gap width")
    fseg_120deg = create_flange_segment(120*deg, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_120deg = calculate_damage(fseg_120deg,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb, "Gap120deg", fseg_120deg, dmg_120deg)


#### Case 6
if Case_6_interpolated:
    print("\nEvaluating Flange Segment Model with gap shape factor 1.5 and no flange tilt ...")
    wb_sf = open_workbook("Case_6-D7500_Tilt-0deg_ShapeFactor-1.5-interpolated.xlsx")
    
    print("... with 30 deg gap width")
    fseg_30deg_sf  = create_flange_segment( 30*deg, 1.5, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_30deg_sf = calculate_damage(fseg_30deg_sf,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sf, "Gap30deg", fseg_30deg_sf, dmg_30deg_sf)
    
    print("... with 60 deg gap width")
    fseg_60deg_sf  = create_flange_segment( 60*deg, 1.5, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_60deg_sf = calculate_damage(fseg_60deg_sf,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sf, "Gap60deg", fseg_60deg_sf, dmg_60deg_sf)
    
    print("... with 90 deg gap width")
    fseg_90deg_sf  = create_flange_segment( 90*deg, 1.5, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_90deg_sf = calculate_damage(fseg_90deg_sf,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sf, "Gap90deg", fseg_90deg_sf,dmg_90deg_sf)
    
    print("... with 120 deg gap width")
    fseg_120deg_sf = create_flange_segment(120*deg, 1.5, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_120deg_sf = calculate_damage(fseg_120deg_sf,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sf, "Gap120deg", fseg_120deg_sf, dmg_120deg_sf)


#### Case 7
if Case_7_interpolated:
    print("\nEvaluating Flange Segment Model with gap shape factor 1.5 and 1 deg flange tilt ...")
    wb_sftt = open_workbook("Case_7-D7500_Tilt-1deg_ShapeFactor-1.5-interpolated.xlsx")
    
    print("... with 30 deg gap width")
    fseg_30deg_sftt  = create_flange_segment( 30*deg, 1.5, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_30deg_sftt = calculate_damage(fseg_30deg_sftt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sftt, "Gap30deg", fseg_30deg_sftt, dmg_30deg_sftt)
    
    print("... with 60 deg gap width")
    fseg_60deg_sftt  = create_flange_segment( 60*deg, 1.5, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_60deg_sftt = calculate_damage(fseg_60deg_sftt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sftt, "Gap60deg", fseg_60deg_sftt, dmg_60deg_sftt)
    
    print("... with 90 deg gap width")
    fseg_90deg_sftt  = create_flange_segment( 90*deg, 1.5, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_90deg_sftt = calculate_damage(fseg_90deg_sftt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sftt, "Gap90deg", fseg_90deg_sftt, dmg_90deg_sftt)
    
    print("... with 120 deg gap width")
    fseg_120deg_sftt = create_flange_segment(120*deg, 1.5, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_129deg_sftt = calculate_damage(fseg_120deg_sftt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_sftt, "Gap120deg", fseg_120deg_sftt, dmg_129deg_sftt)


#### Case 8
if Case_8_interpolated:
    print("\nEvaluating Flange Segment Model with sinusoidal gap shape and 1 deg flange tilt ...")
    wb_tt = open_workbook("Case_8-D7500_Tilt-1deg_ShapeFactor-1.0-interpolated.xlsx")
    
    print("... with 30 deg gap width")
    fseg_30deg_tt  = create_flange_segment( 30*deg, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_30deg_tt = calculate_damage(fseg_30deg_tt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_tt, "Gap30deg", fseg_30deg_tt, dmg_30deg_tt)
    
    print("... with 60 deg gap width")
    fseg_60deg_tt  = create_flange_segment( 60*deg, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_60deg_tt = calculate_damage(fseg_60deg_tt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_tt, "Gap60deg", fseg_60deg_tt, dmg_60deg_tt)
    
    print("... with 90 deg gap width")
    fseg_90deg_tt  = create_flange_segment( 90*deg, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_90deg_tt = calculate_damage(fseg_90deg_tt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_tt, "Gap90deg", fseg_90deg_tt, dmg_90deg_tt)
    
    print("... with 120 deg gap width")
    fseg_120deg_tt = create_flange_segment(120*deg, tilt_angle=1*deg, macro_geometric_factor=macro_geometric_factor,k_shell_option=k_shell_option)
    dmg_129deg_tt = calculate_damage(fseg_120deg_tt,macro_geometric_factor=macro_geometric_factor)
    flangesegment_to_excel(wb_tt, "Gap120deg", fseg_120deg_tt, dmg_129deg_tt)
