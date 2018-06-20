#!/bin/sh

#python ffff_politifact.py cnn_politifact 2012; python run_cnn_predict_snopes_politics.py cnn_politifact 2012 ; python analyze_result.py 
#python ffff_politifact.py cnn_politifact 2013; python run_cnn_predict_snopes_politics.py cnn_politifact 2013 ; python analyze_result.py 
#python ffff_politifact.py cnn_politifact 2014; python run_cnn_predict_snopes_politics.py cnn_politifact 2014 ; python analyze_result.py 
#python ffff_politifact.py cnn_politifact 2015; python run_cnn_predict_snopes_politics.py cnn_politifact 2015 ; python analyze_result.py 
#python ffff_politifact.py cnn_politifact 2016; python run_cnn_predict_snopes_politics.py cnn_politifact 2016 ; python analyze_result.py 
#python ffff_politifact.py cnn_politifact 2017; python run_cnn_predict_snopes_politics.py cnn_politifact 2017 ; python analyze_result.py 
#python ffff_politifact.py cnn_politifact 2015,2016,2017; python run_cnn_predict_snopes_politics.py cnn_politifact 2015,2016,2017 ; python analyze_result.py 
python ffff_politifact.py cnn_politifact 2012,2013,2014,2015,2016,2017; python run_cnn_predict_snopes_politics.py cnn_politifact 2014,2015,2016,2017 ; python analyze_result.py 
