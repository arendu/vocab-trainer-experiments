#dev: ave model loss:64.264,20.684,28,986 p_u:0.292,0.250,986 p_c:0.471,0.242,453 p_ic:0.139,0.123,533 p_ict:0.328,0.193,533 acc:0.412 params9!/usr/bin/env python
import glob
import pdb
import re
__author__ = 'arenduchintala'
"""
ave total loss:174.348 p_u:0.303,0.401 p_c:0.504,0.426 p_ic:0.135,0.285 p_ict:0.340,0.399 params:4.334,4.332--5.001,4.999--0.471,0.463--5.004,4.996
"""
def scan_file(fs):
    min_loss = (1000000, None, None, 10000000)
    max_p_u = (0, None, None, 0)
    max_acc = (0, None, None, 0)
    max_p_c = (0, None, None)
    max_p_ic = (0, None, None)
    min_p_ict = (1000000, None, None)
    max_p_c_ict = (0, None, None)
    for f in glob.glob(fs):
        print 'scaning', f
        content = open(f, 'r').readlines()
        dev_content = [c for c in content if c.startswith('dev:')]
        test_content = [c for c in content if c.startswith('test:')]
        #dev_content = [c for idx,c in enumerate(content) if idx % 2 ==0]
        #train_content = [c for idx,c in enumerate(content) if idx % 2 ==0]
        items = re.split(r'(\s+|:)', dev_content[-3])
        test_items = re.split(r'(\s+|:)', test_content[-3])
        items = [i for i in items if i.strip() != '' and i.strip() !=':']
        items.pop(0)
        items = [i.split(',')[0] for i in items]
        loss_on_dev = float(items[3]) #test loss
        acc_on_dev = float(items[13])
        test_items = [i for i in test_items if i.strip() != '' and i.strip() !=':']
        test_items.pop(0)
        test_items = [i.split(',')[0] for i in test_items]
        loss_on_test = float(test_items[3])
        acc_on_test = float(test_items[13])
        if loss_on_dev < min_loss[0]:
            min_loss = (loss_on_dev, len(dev_content) - 3, f, loss_on_test)
        if acc_on_dev > max_acc[0]:
            max_acc = (acc_on_dev, len(dev_content) - 3, f, acc_on_test)
        dev_p_u = float(items[5])
        test_p_u = float(test_items[5])
        if dev_p_u > max_p_u[0]:
            max_p_u = (dev_p_u, len(dev_content) - 3, f, test_p_u)

        """
        for idx,dc in enumerate(dev_content):
            items = re.split(r'(\s+|:)', dc)
            test_items = re.split(r'(\s+|:)', test_content[idx])
            items = [i for i in items if i.strip() != '' and i.strip() !=':']
            test_items = [i for i in test_items if i.strip() != '' and i.strip() !=':']
            items.pop(0)
            test_items.pop(0)
            items = [i.split(',')[0] for i in items]
            test_items = [i.split(',')[0] for i in test_items]
            loss_on_dev = float(items[3]) #test loss
            acc_on_dev = float(items[13])
            acc_on_test = float(test_items[13])
            loss_on_test = float(test_items[3])
            if loss_on_dev < min_loss[0]:
                min_loss = (loss_on_dev, idx, f, loss_on_test)
            if acc_on_dev > max_acc[0]:
                max_acc = (acc_on_dev, idx, f, acc_on_test)
            dev_p_u = float(items[5])
            test_p_u = float(test_items[5])
            if dev_p_u > max_p_u[0]:
                max_p_u = (dev_p_u, idx, f, test_p_u)
            p_c = float(items[7])
            if p_c > max_p_c[0]:
                max_p_c = (p_c, idx, f)
            p_ic = float(items[9])
            if p_ic > max_p_ic[0]:
                max_p_ic = (p_ic, idx, f)
            p_ict = float(items[11])
            if p_ict < min_p_ict[0]:
                min_p_ict = (p_ict, idx, f)
            p_c_ict = p_c - p_ict
            if p_c_ict > max_p_c_ict[0]:
                max_p_c_ict = (p_c_ict, idx, f)
        """
    print 'min_loss:'.ljust(20), "%.4f" % min_loss[0], min_loss[1], min_loss[2], min_loss[3]
    print 'max_acc:'.ljust(20), "%.4f" % max_acc[0], max_acc[1], max_acc[2], max_acc[3]
    print 'max_pu:'.ljust(20), "%.4f" % max_p_u[0], max_p_u[1], max_p_u[2], max_p_u[3]
    #print 'max_p_u:'.ljust(20), "%.4f" % max_p_u[0], max_p_u[1], max_p_u[2]
    #print 'max_p_c:'.ljust(20), "%.4f" % max_p_c[0], max_p_c[1], max_p_c[2]
    #print 'max_p_ic:'.ljust(20), "%.4f" % max_p_ic[0], max_p_ic[1], max_p_ic[2]
    #print 'min_p_ict:'.ljust(20), "%.4f" % min_p_ict[0], min_p_ict[1], min_p_ict[2]
    #print 'max_p_c_diff_ict:'.ljust(20), "%.4f" % max_p_c_ict[0], max_p_c_ict[1], max_p_c_ict[2]
    return min_loss, max_p_u, max_p_c, max_p_ic, min_p_ict, max_p_c_ict, max_acc


if __name__ == '__main__':
    for k in ["all"]: #100 90 80 70 60 50 40 30 20 10".split():
        print '\n',k
        for gm in [3, 1, 0]:
            for gt in ["0"]:
                for t in [0]:
                    for i in "0 1 3".split():
                        t = str(t)
                        gm = str(gm)
                        #simple.m.m3.u.rms.r.0.001.gt.sign.c.free.bl.0.0.gm.g0.t.t0.log
                        fs = "./simple.m.m" + i + ".u.rms.r.0.001.gt." + gt + ".*bl.0.0.gm.g" + str(gm) + ".t.t" + t + ".top_" + k +".*log"
                        print 'best m', i, t
                        min_loss, max_p_u, max_p_c, max_p_ic, min_p_ict, max_p_c_ict, max_acc = scan_file(fs)
    exit(0)
    print "top k"
    for k in "1500 800 400 200 100 90 80 70 60 50 40 30 20 10".split():
        print '\n',k
        for gm in [1]:
            for gt in ["0"]:
                for t in [0]:
                    for i in "3".split():
                        t = str(t)
                        gm = str(gm)
                        #simple.m.m3.u.rms.r.0.001.gt.sign.c.free.bl.0.0.gm.g0.t.t0.log
                        fs = "./simple.m.m" + i + ".u.*.r.*.gt." + gt + ".*bl.0.0.gm.g" + str(gm) + ".t.t" + t + ".top_" + k +".*log"
                        print 'best m', i, t
                        min_loss, max_p_u, max_p_c, max_p_ic, min_p_ict, max_p_c_ict, max_acc = scan_file(fs)

