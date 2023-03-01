import warnings
warnings.filterwarnings('ignore')
from pandas_datareader import data as pdr
import yfinance as yfin
yfin.pdr_override()

# CSVを読み込み用
import pandas as pd
# Mean Absolute Error(MAE)用
from sklearn.metrics import mean_absolute_error
# Root Mean Squared Error(RMSE)用
from sklearn.metrics import mean_squared_error
import numpy as np
import datetime

from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import accuracy_score
import csv

def xgboost():
    # 銘柄ファイルを読み込み
    df = pd.read_csv('nikkei_sbi.csv')
    # # 出力ファイルの先頭行
    ret_l = []
    for index,row in df.iterrows():
        # 指定した株価を取得
        end_date = datetime.datetime.today().strftime("%Y-%m-%d")
        start_date = (datetime.datetime.today() - datetime.timedelta(days=365+31)).strftime("%Y-%m-%d")
        holder_name = str(row[0])+'.T' 
        finence_name = str(row[1])
        print(start_date, end_date, holder_name, finence_name)
        df = pdr.get_data_yahoo(holder_name, start_date, end_date)

        # 学習用パラメータ設定
        df["Diff"] = df.Close.diff() #　前日のCloseとの比較
        df["SMA_5"] = df.Close.rolling(window=5).mean()
        df["SMA_25"] = df.Close.rolling(window=25).mean()
        df["SMA_40"] = df.Close.rolling(window=40).mean()
        df["Force_Index"] = df["Close"] * df["Volume"]

        df = df.drop(
            ["Open", "High", "Low", "Adj Close"],
            axis=1,
        ).dropna()

        df["Close_tom"] = df.Close.shift(-1) #明日の終値

        # データセット作成
        row = len(df)
        range_day =15
        df_train = df[0:row-range_day]
        df_test = df[row-range_day:row-1]#最後から5行
        df_end = df[row-1:row]## 一番最後の行
        df_train_X = df_train.drop(["Close_tom"], axis=1).values # SMA_5, Force_index
        df_train_y = df_train["Close_tom"].values # y
        df_test_X = df_test.drop(["Close_tom"], axis=1).values # SMA_5, Force_index
        df_test_y = df_test["Close_tom"].values #
        df_end_X = df_end.drop(["Close_tom"], axis=1).values 

        # 学習モデル構築
        clf = xgb.XGBRegressor(objective='reg:squarederror')
        if len(df_train_X) == 0 or len(df_train_y) == 0:
            continue
        clf.fit(
            df_train_X,
            df_train_y,
        )

        # y_pred = clf.predict(df_test_X)
        # df_result = df_test
        # df_result["pred"] = 0
        # df_result["pred"] = y_pred
        # df_result["error_diff"]=abs(df_result["pred"] - df_result["Close_tom"])
        # df_result["error_diff_pm"]=df_result["pred"] - df_result["Close_tom"]
        # df_result["diff_range"]=abs(df_result["pred"] - df_result["Close"])

        # 今日の株価予測
        today_pred = clf.predict(df_end_X)
        df_result_today = df_end
        df_result_today["pred"] = 0
        df_result_today["pred"] = today_pred
        df_result_today["diff_range"]= df_result_today["pred"] - df_result_today["Close"]
        # max = df_result['error_diff_pm'].max()
        # min = df_result['error_diff_pm'].min()
        # mae = '{:.1f}'.format(mean_absolute_error(df_test_y, y_pred))
        #print(today_pred)
        flg_today = 0

        close_val_yesterday = '{:.1f}'.format((df_result_today.iloc[0])["Close"])
        pred_val_today = '{:.1f}'.format((df_result_today.iloc[0])["pred"])
        diff_y2t = (df_result_today.iloc[0])["diff_range"]

        if float(close_val_yesterday) < float(pred_val_today):
            flg_today = 1
        diff_y2t = '{:.1f}'.format(diff_y2t)
        out_l = [finence_name,holder_name,close_val_yesterday,pred_val_today,0,flg_today,0,diff_y2t,0]
        ret_l.append(out_l)
    with open('nikkei_yosoku.csv', 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(ret_l)
    return ret_l

        # print_flg = 0
        # if diff_y2t > 0 and float(pred_val_today) < 3000 and float(diff_y2t) > 0 and float(mae) > 0:
        #     tmp_row = [holder_name,finence_name,close_val_yesterday ,pred_val_today,  diff_y2t, mae, max,min]
        #     print(tmp_row)
        #     print_flg = 1

        # if diff_y2t > 0:
        #     diff_y2t = '+{:.1f}'.format(diff_y2t)
        # else:
        #     diff_y2t = '{:.1f}'.format(diff_y2t)

        # if max > 0:
        #     max  = '+{:.1f}'.format(max)
        # else:
        #     max = '{:.1f}'.format(max)
        # if min > 0:
        #     min  = '+{:.1f}'.format(min)
        # else:
        #     min = '{:.1f}'.format(min)
        
        # if print_flg == 1:
        #     print("----------------------------------------------------------------------\n")
        #     print(
        #         "【今日の株価予測】　\n\n" + \
        #         "銘柄 : "+ finence_name +"　("+holder_name+")\n\n"+ 
        #         "昨日の株価　(終値) :　"+ close_val_yesterday +"円\n" \
        #         "今日の予想株価　（終値）　：　"+ str(pred_val_today) +"円 ("+ diff_y2t + "円)\n\n" \

        #         "直近 "+str(range_day)+" 営業日の予測誤差\n" \
        #         "(平均　: ±"+mae+ ",  最大　: "+max+",  最小　: "+min+")"
        #     )
        #     print("\n-----------------------------------------------------------------------")

