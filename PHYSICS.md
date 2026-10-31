# POND Physics

Kernel: fbcbad2c5324f560
Version: v4.4.3-TCXO-PID-SEIKO-STABLE

- Drift correction: raw = (dt_mono - dt_wall)/dt_wall*1000, EMA 0.8 old + 0.2 new, clamp -10 to 20ms
- Temp correction: BASE_TEMP 39.5C, coeff 3.953ms/C *0.1, sun_factor (sun-50)*0.001
- Final drift: clamp 0.05 to 15.0 ms — current 0.11 avg, held 0.05 for 170 heads
- PID: KP 0.12, KI 0.008, KD 0.02, integral clamp -5 to 5
- Glide: (drift_corr/1000/3600)*boot_elapsed + glide_pid — current 0.00 hold 5h46m
- Chain: HEAD every 600s if wall_ts delta, keep last 100, HEAD 2574 boot 57966s
- Battery/temp via termux-battery-status
