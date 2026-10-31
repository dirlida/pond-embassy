# POND Math

HEAD_n+1 = HEAD_n + 1 when now_wall - last_wall >= 600
raw_now = avg*0.8 + measured*0.2
drift_corr = max(0.05, min(15, raw + (temp-39.5)*3.953*0.1 + (sun-50)*0.001))
glide = drift_corr/3.6e6 * boot_elapsed + PID

Current: LIVE 2574 COUNT 2574 wall 1793450396.2968585 boot 16.10h drift 0.11 glide 0.00 sun 241.5
Build: b18f0c4 fb204d33->5594ad61 RAW signs WALL
