#!/usr/bin/env python
import argparse
import sys
import codecs
import numpy as np
import theano
from code.data_reader import read_data
from code.datahelper import DataHelper
from code.recurrent_loglinear import RecurrentLoglinear
from code.eval_tools import disp_eval, pad_start
from code.my_utils import save_obj, load_obj

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

__author__ = 'arenduchintala'

if theano.config.floatX == 'float32':
    floatX = np.float32
    intX = np.int32
else:
    floatX = np.float64
    intX = np.int64

if __name__ == '__main__':
    np.random.seed(124)
    sys.setrecursionlimit(50000)
    s_list = "0 1 2 3 4".split()
    opt= argparse.ArgumentParser(description="write program description here")
    opt.add_argument('-f', action='store', dest='feature', default='p.w.pre.suf.c')
    opt.add_argument('-k', action='store', dest='top_k', default='top_all')
    opt.add_argument('-r', action='store', dest='reg', default=0.01, type=float)
    opt.add_argument('--gt', action='store', dest='grad_transform', default="0")
    opt.add_argument('--bl', action='store', dest='interpolate_bin_loss', default=0.5, type=float)
    opt.add_argument('-u', action='store', dest='grad_update', default="rms")
    opt.add_argument('-m', action='store', dest='model', default="m0")
    opt.add_argument('-g', action='store', dest='grad_model', default="g0")
    opt.add_argument('-c', action='store', dest='clip', default="free")
    opt.add_argument('-t', action='store', dest='temp', default="t0")
    opt.add_argument('--st', action='store', dest='save_trace', default=None)
    opt.add_argument('--sm', action='store', dest='save_model', default=None)
    opt.add_argument('--train', action='store', dest='training_data', default='./data/data_splits/train.strata.0.data', required=True)
    options = opt.parse_args()
    events_file = './data/content/fake-en-medium.' + options.feature  +'.event2feats'
    feats_file = './data/content/fake-en-medium.' + options.feature  +'.feat2id'
    actions_file = './data/content/fake-en-medium.mc.tp.mcr.tpr.actions'
    dh = DataHelper(events_file, feats_file, actions_file)
    print 'training strata', options.training_data
    TRAINING_SEQ = read_data(options.training_data, dh)
    s_num = options.training_data.split('.')[-2]
    s_name = options.training_data.split('.')[-4].split('/')[-1]
    s_rest = '/'.join(options.training_data.split('/')[:-1]) + '/'
    print s_rest, 's_rest'
    print s_name, 's_name'
    print s_num, 's_num'
    s_dev_nums = s_list[s_list.index(s_num) - 1: s_list.index(s_num)] + s_list[s_list.index(s_num) + 1: s_list.index(s_num) +2]
    DEV_SEQ = []
    for s_dev_num in s_dev_nums:
        print s_rest, s_name, s_dev_num
        d_f = s_rest + s_name + '.strata.' + s_dev_num + '.data'
        print 'using dev', d_f
        DEV_SEQ += read_data(d_f, dh)

    _theta_0 = np.zeros((dh.FEAT_SIZE,)).astype(floatX)
    _decay = 0.001
    _learning_rate = 0.1 #only used for sgd
    _clip = options.clip == "clip"
    sll = RecurrentLoglinear(dh, 
                        u = options.grad_update,
                        reg = (options.reg / len(TRAINING_SEQ)), 
                        grad_transform = options.grad_transform,
                        learning_model = options.model,
                        grad_model = options.grad_model,
                        clip = _clip,
                        temp_model = options.temp,
                        grad_top_k = options.top_k,
                        interpolate_bin_loss = options.interpolate_bin_loss)
    prev_dl = 1000000.0000
    prev_dacc = 0.0
    best_dl = 1000000.000
    prev_dpu = 0.0
    improvement = []
    for epoch_idx in xrange(100):
        lr = _learning_rate * (1.0  / (1.0 + _decay * epoch_idx))
        lr = lr if options.grad_update == "sgd" else (0.05 / len(TRAINING_SEQ))
        shuffle_ids = np.random.choice(xrange(len(TRAINING_SEQ)), len(TRAINING_SEQ), False)
        sys.stderr.write('-')
        for r_idx in shuffle_ids[:]:
            sys.stderr.write('.')
            _X, _Y, _YT, _O, _S = TRAINING_SEQ[r_idx]
            _SM1 = pad_start(_S)
            seq_losses, seq_thetas, seq_y_hats = sll.do_update(_X, _Y, _YT, _O, _S, _SM1, _theta_0, lr)
            _params = sll.get_params()
            #print '_params in main', _params
            _max_p = []
            if np.isnan(seq_losses):
                raise Exception("loss is nan")
            if np.isnan(seq_y_hats).any():
                raise Exception("y_hat has nan")
            for _p in _params:
                if np.isnan(_p).any():
                    raise Exception("_params is nan")
                _max_p.append(np.max(_p))
        msg_d,dl,dpu,dacc = disp_eval(DEV_SEQ, sll, dh, options.save_trace, epoch_idx) 
        print 'dev:', msg_d
        msg_t, tl, tpu, train_acc = disp_eval(TRAINING_SEQ, sll, dh, None, None)
        print 'train:', msg_t
        if dacc > prev_dacc and options.save_model is not None:
            save_obj(sll, options.save_model) 
            sll.save_weights(options.save_model + '.json_params')
            if 0 == 1:
                loaded_ll = RecurrentLoglinear(dh, 
                                u = options.grad_update,
                                reg = (options.reg / len(TRAINING_SEQ)), 
                                grad_transform = options.grad_transform,
                                learning_model = options.model,
                                grad_model = options.grad_model,
                                clip = _clip,
                                temp_model = options.temp,
                                grad_top_k = options.top_k,
                                interpolate_bin_loss = options.interpolate_bin_loss, 
                                saved_weights = options.save_model + '.json_params')

                loaded_msg_d, loaded_dl, loaded_dpu, loaded_dacc = disp_eval(DEV_SEQ, loaded_ll, dh, None, None)
                print 'loaded_dev:', loaded_msg_d
                loaded_msg_t, loaded_dl, loaded_dpu, loaded_dacc = disp_eval(TRAINING_SEQ, loaded_ll, dh, None, None)
                print 'loaded_train:', loaded_msg_t

                pickle_loaded_ll = load_obj(options.save_model)
                loaded_msg_pd, loaded_dl, loaded_dpu, loaded_dacc = disp_eval(DEV_SEQ, pickle_loaded_ll, dh, None, None)
                print 'pickle_loaded_dev:', loaded_msg_pd
                loaded_msg_pt, loaded_dl, loaded_dpu, loaded_dacc = disp_eval(TRAINING_SEQ, pickle_loaded_ll, dh, None, None)
                print 'pickle_loaded_train:', loaded_msg_pt

                assert msg_d == loaded_msg_d == loaded_msg_pd
                assert msg_t == loaded_msg_t
            else:
                pass
        else:
            pass

        improvement.append((1 if dacc > prev_dacc else 0))
        if np.sum(improvement[-2:]) == 0 and len(improvement) > 10:
            break
        else:
            pass
        prev_dacc = dacc
