import os
MODEL="attention_rnn_2.mag"
PRIMER="/home/meloaid/melo-aid-backend/routes/stereohrts-trimmed.mid"
def gen_melody(PRIMER):
    os.system("python3 /home/meloaid/melo-aid-backend/magenta/magenta/models/melody_rnn/melody_rnn_generate.py --config='lookback_rnn' --bundle_file=/home/meloaid/melo-aid-backend/magenta/{} --output_dir=/home/meloaid/melo-aid-backend/magenta/generated --num_outputs=3 --hparams='batch_size=64,rnn_layer_sizes=[64,64]' --num_steps=160 --primer_midi={}".format(MODEL,PRIMER))

