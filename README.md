# RICO Dataset

This README provides the basic information regarding the RICO dataset.

For more information, please refer to the original paper.

This dataset is published and maintained by **SINTEF AS Digital**.

**Visiting Address**: Strindvegen 4, 7034 Trondheim  
**E-mail**: info@sintef.no  
**Website**: https://www.sintef.no/sintef-digital/

## Methodology

The RICO dataset comprises high-frequency measurements from sensors in the Zero Energy Building (ZEB) Test Cell. Two types of sensors are utilized:
1. Internal sensors that measure temperature, humidity, and radiation
2. External sensors collected from the building's dedicated weather station. 

We observe these features under two sets of constraints : 
  1. External constraints: elements outside of our control such as environment temperature, wind, weather...
  2. Controled constraints: eentilation heating and cooling, radiator heating and cooling

Data were collected across five distinct phases, lasting from a few days to 17 days over a period of 11 months, capturing diverse weather conditions. This resulted in 305 multivariate time-series, each four hours long and 80 features rich. All measurements were recorded at 10 samples per minute and normalized to a 1-minute sampling interval for consistency.

More detail about the Phases' specificities are detailed in the section `Acquisition Phases`. 

**Other information**:
- **type**: tabular
- **sampling_rate**: 1/min
- **n_features**: 80
- **length**: Depending on the acquisition phase (ranges from 10 to 100+)



## Overview

### File Structure
The dataset is stored in a shallow folder structure, in the open [hdf5](https://www.hdfgroup.org/solutions/hdf5/) format.

\- root folder  
| - README.md  
| - RICO_Acquisition_1_07-2023.hdf  
| - RICO_Acquisition_2_10-2023.hdf  
| - RICO_Acquisition_3_01-2024.hdf  
| - RICO_Acquisition_4_02-2024.hdf  
| - RICO_Acquisition_5_05-2024.hdf  


### Sample from processed dataframe

| _time                     | Acq ... Phase | Scheduler Step | Flag | B.RTD6 | ... |   WS1_Wind_speed |   BT.SIC_25 |
|:--------------------------|--------------:|---------------:|:----:|-------:|----:|-----------------:|------------:|
| 2023-07-26 11:01:00+00:00 |             1 |              0 |  1   |   26.5 | ... |             26.6 |        26.6 |
| 2023-07-26 11:02:00+00:00 |             1 |              0 |  1   |   26.6 | ... |             26.8 |        26.8 |
| 2023-07-26 11:03:00+00:00 |             1 |              0 |  1   |   26.8 | ... |             27.3 |        27.3 |
| 2023-07-26 11:04:00+00:00 |             1 |              0 |  1   |   26.9 | ... |             27.8 |        27.8 |
| 2023-07-26 11:05:00+00:00 |             1 |              0 |  1   |   27.0 | ... |             28.3 |        28.3 |


## Acquisition Phases

### RICO 1
- **N_points**: 102
- **Start date**: 26/07/2023 13:01:00
- **End date**: 12/08/2023 13:00:00
- **Run type**: 4h runs
- **Notes**: 
    - Untuned PIDs
    - Should consider manual points removal

### RICO 2

- **N_points**: 60
- **Start date**: 20/10/2023 13:01:00
- **End date**: 30/10/2023 13:00:00
- **Run type**: 3h + 1h runs (with 1h downtime)
- **Notes**:
  - PID Tuning: ~ OK
  - No control of cell A
  - Ran in cell B
  - BUG software: Setpoints don't upload to DB, needs to be fixed

### RICO 3

- **N_points**: 24 reduced to 6 in short version
- **Start date**: 22/01/2024 14:00:00 or 14:30:00 if short version
- **End date**: 26/01/2024 13:59:00
- **Run type**: 3h + 1h runs (with 1h downtime)
- **Notes**:
  - PID Tuning: ~ OK
  - No control of cell A
  - Ran in cell B
  - Setpoints recording: NOK
  - Mistake: 
    - Normal version contains 6 points of length 12 hours + 4h downtime
    - Short version contains 6 points of length 4 hours 
    - Explanation: Ran in 4* (3h + 1h). Scheduler frequency was set to 4h instead of 1, so each points lasts for 4*4 = 16h.

### RICO 4
- **N_points**: 60
- **Start date**: 29/01/2024 16:01:00
- **End date**: 07/02/2024 16:00:00
- **Run type**: 4h runs
- **Notes**
    - Current version stops at 2024-02-02T12:00:00
    - Setpoints recording: OK

### RICO 5
- **N_points**: 60
- **Start date**: 08/05/2024 09:01:00
- **End date**: 18/05/2024 09:00:00
- **Run type**: 4h runs
- **Notes**
    - All OK ✅

## Detail of features

### 1. Controls

These are the features used to control the different technical systems (i.e., heating and cooling), for common actuators and cell B actuators.

#### 0.1 Acquisition parameters

- `Acquisition Phase`$\in \mathbb{N}$ : the n° of acquisition phase
- `Scheduler Step` $\in \mathbb {N}$ :the scheduler step. Also corresponds to the N° of point within the acquisiton phase
- `Flag` $\in \{0,1\}$: 1 for normal, 0 for abnormal point

#### 1.1 Radiator Heating

- SB47 Controls: `SB47`, `pid.SB47.setpoint`, `pid.SB47.enabled`
- JP41 Main Hot Water Pump: `JP41_volumeFlow`, `JP41_setpoint`, `JP41_head`
- JP410 Hot Water Pump Cell B: `JP410_volumeFlow`, `JP410_setpoint`, `JP410_head`
- RTD420 (Inlet): Temperatures of the hot water inlet circuit in cell B
- RTD509 (Outlet): Temperatures of the hot water outlet circuit in cell B

#### 1.2 Fan Coil

- SB46 Control: `SB46`, `pid.SB46.setpoint`, `pid.SB46.enabled`
- JP40 Main Cold Water Pump: `JP40_volumeFlow`, `JP40_setpoint`, `JP40_head`
- JP49 Cold Water Pump Cell B: `JP49_volumeFlow`, `JP49_setpoint`, `JP49_head`
- SSR6: Switch of the fancoil fan
- RTD417 (Inlet): Temperatures of the cold water inlet circuit in cell B
- RTD508 (Outlet): Temperatures of the cold water outlet circuit in cell B

#### 1.3 Ventilation Heating

- EC3 Control: `EC3`, `pid.EC3.enabled`, `pid.EC3.setpoint`
- RTD410.T (Upstream)
- RTD406A (Downstream)
- B.ASTRHT2.T (Inlet in the room)

#### 1.4 Ventilation Cooling

- SB43 Control: Same as above
- JP40 Main Cold Water Pump: Same as above
- JP44 Cold Water Pump Cooling Battery in the Ventilation Duct: Same as above
- RTD410.T (Upstream)
- RTD406A (Downstream)
- B.ASTRHT2.T (Inlet in the room)

### 2. Room Temperature

- B.RTD1 [C]: Cell A Pt100 thermometer centre of the room 10 cm from the floor
- B.RTD2 [C]: Pt100 60 cm from the floor
- B.RTD3 [C]: Pt100 110 cm
- B.RTD6 [C]: Glober thermometer 160 from the floor
- BT.15: Fast moving thermometer, 180cm from floor

### 3. Weather 

- B.SIM1: Solar radiation on cell B window [w/m^2]
- WS1 - Solar radiation: Solar radiation on the horizontal plan. [w/m^2]
- 0.SIM1: Solar radiation on the roof slope (on the same mast as the WS)
- 0.SIM2: Solar radiation on the vertical plane (on the same mast as the WS)
- 0.SIM3: Solar radiation impinging the facade (important feature)

## License

This project is licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) License.

You are free to:

- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:

- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
For more details, please refer to the Creative Commons Attribution 4.0 International License.