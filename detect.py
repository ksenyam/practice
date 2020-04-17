from __future__ import division
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


class anom_detect():
    def __init__(self,method='average',window=5,max_outliers=None,alpha=0.05,mode='same'):
        self.method = method
        self.window = window
        self.max_outliers = max_outliers
        self.alpha = alpha
        self.mode = mode

    def moving_average(self,f_t):
        if type(f_t) is not np.ndarray:
            raise TypeError\
                ('Expected one dimensional numpy array.')

        f_t = f_t.flatten()
        window = self.window
        mode = self.mode
        g_t = np.ones(int(window))/float(window)
        # Deal with boundaries with atleast lag/2 day window
        #mode = 'same'
        rolling_mean = np.convolve(f_t,g_t,mode)
        self.rolling_mean = rolling_mean

        return rolling_mean

    def deviation_stats(self,df, col):
 
        df['mean_count'] = self.rolling_mean
        df['residual'] = df[col] - self.rolling_mean
        std_resid = np.std(df.residual)
        df['pos_std'] = df.mean_count + std_resid
        df['neg_std'] = df.mean_count - std_resid
        df['pos_std_2'] = df.mean_count + 2*std_resid
        df['neg_std_2'] = df.mean_count - 2*std_resid
        return df

    def normality(self):
        if self.results is not None:
            df = self.results
            fig, (ax1, ax2) = plt.subplots(1, 2,figsize=(10, 6))
            x = df.residual.values
            re = stats.probplot(x, plot=ax2)
            ax1.hist(df.residual,bins=100);
            ax1.set_title('Distribution of Residuals');
        else:
            raise NameError\
                ('The moving average for the data has not yet been computed.  Run moving_averge or evaluate prior to normality.')


    def esd_test(self,df_in):
        ind = list(df_in.index)
        x = list(df_in.values)
        outliers = []
        res_lst = [] # ESD Test Statistic for each k anomaly
        lam_lst = [] # Critical Value for each k anomaly
        n = len(x)

        if self.max_outliers is None:
            self.max_outliers = len(x)

        for i in range(1,self.max_outliers+1):
            x_mean = np.mean(x)
            x_std = np.std(x,ddof=1)
            res = abs((x - x_mean) / x_std)
            max_res = np.max(res)
            max_ind = np.argmax(res)
            p = 1 - self.alpha / (2*(n-i+1))
            t_v = stats.t.ppf(p,(n-i-1)) # Get critical values from t-distribution based on p and n
            lam_i = ((n-i)*t_v)/ np.sqrt((n-i-1+t_v**2)*(n-i+1)) # Calculate critical region (lambdas)
            res_lst.append(max_res)
            lam_lst.append(lam_i)
            if max_res > lam_i:
                outliers.append((ind.pop(max_ind),x.pop(max_ind)))
        # Record outlier Points
        outliers_index = [x[0] for x in outliers]

        ESD_stats = pd.DataFrame()
        ESD_stats['ESD Test Statistic'] = res_lst
        ESD_stats['Critical Value'] = lam_lst
        self.ESD_stats = ESD_stats

        return outliers_index

 
    def plot(self,data_label=None, left=None,right=None,bottom=None,top=None):
        fig, ax = plt.subplots(len(self.cols), 1, sharex=True, figsize=(15, 8))
        cnt = 0
        for col in self.results:
            df = self.results[col]
            anoma_points = self.anoma_points[col]
            ax[cnt].plot(list(df.index),df.iloc[:,0],'k.',label=data_label)
            ax[cnt].plot(list(df.index),df.mean_count,c="green",label='Moving Average')
            ax[cnt].fill_between(df.index, df.pos_std_2,df.neg_std_2, color='green', alpha=0.1,label='2Sigma')
            ax[cnt].plot(list(anoma_points.index), anoma_points.iloc[:,0],'r.', label='Anomalous Points')
            
            
            ax[cnt].set_ylabel(data_label)
            ax[cnt].set_xlim(left=left,right=right)
            ax[cnt].set_ylim(bottom=bottom,top=top)
            cnt += 1
        plt.suptitle(", ".join(list(self.results.keys())))
        plt.xlabel('weeks')
        plt.legend(bbox_to_anchor=(1.05, .5));

    def evaluate(self,data,anom_detect=True):
        # Check data is in the right format and right order and dimension
        # Check for example if there are large gaps in the data.
        

        df = pd.DataFrame(data)
        df.sort_index()
        self.cols = [i for i in df.columns if i != df.index.name]
        if df.shape[1] < 1:
            raise IndexError\
                ('Insufficient dimensions provided, input data needs time and value columns.')
        self.results = {}
        self.anoma_points = {}
        for col in self.cols:
            if self.method == 'average':
                data_points = df[col].values
                
                self.moving_average(data_points)
                df1 = self.deviation_stats(df[col].to_frame(), col)
                self.results[col] = df1

            if anom_detect:
                outliers_index = self.find_2std(col)
                #outliers_index = self.esd_test(df[['residual']])
                anoma_points = pd.DataFrame(df[[col]].iloc[outliers_index,0].sort_index())
                self.anoma_points[col] = anoma_points

            

        
        
        
    def find_2std(self, col):
        vals = []
        for row in self.results[col].iterrows():
            if row[1][col] > row[1]["pos_std_2"] or  row[1][col] < row[1]['neg_std_2']:
                vals.append(row[0])
        return vals
            
            
            
            
            
            