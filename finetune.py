import gpt_2_simple as gpt2

#Select a gpt2 model size, options are "117M", "345M" and "774M"
model_name = "117M"
dataset = 'sampledata.txt'
run_name = 'sampledata'
# model is saved into current directory under /models/model_name/
gpt2.download_gpt2(model_name=model_name)   

#train new model

sess = gpt2.start_tf_sess()
gpt2.finetune(sess,
              dataset,
              model_name=model_name,
              run_name=run_name,
              steps=1000, # steps is max number of training steps
              save_every=50,
              sample_every=50)
gpt2.generate(sess)


#train existing model
'''
sess = gpt2.start_tf_sess()
gpt2.finetune(sess,
              dataset,
              model_name=model_name,
              run_name=run_name,
              steps=1000, # steps is max number of training steps
              save_every=50,
              sample_every=50,
              overwrite=True)
gpt2.generate(sess)
'''
