import os
MODEL="attention_rnn.mag"
PRIMER="/home/meloaid/melo-aid-backend/routes/stereohrts-trimmed.mid"
def gen_melody(PRIMER):
    os.system("python3 magenta/magenta/models/melody_rnn/melody_rnn_generate.py --config='lookback_rnn' --bundle_file=/home/meloaid/melo-aid-backend/magenta/{} --output_dir=/home/meloaid/melo-aid-backend/magenta/generated --num_outputs=10 --num_steps=128 --primer_midi={}".format(MODEL,PRIMER))

