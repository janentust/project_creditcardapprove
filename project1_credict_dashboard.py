#os.getcwd()
#/Users/JaneChang/Desktop/Janet/ProjectForPython/Project1_credictcardapprove/project1_credict_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import os
import kaggle
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import altair as alt

#下載kaggle資料
#kaggle.api.authenticate()
#kaggle.api.dataset_download_files('rikdifos/credit-card-approval-prediction', path='.', unzip=True)

#read data
application = pd.read_csv("./application_record.csv")
application['DAYS_BIRTH'] =-(application['DAYS_BIRTH']/365).astype('int')
#application['DAYS_EMPLOYED'] =-(application['DAYS_EMPLOYED']/365).astype('int')
#application.dtypes
#application.head(10)


record = pd.read_csv("./credit_record.csv")
#record.head(10)

application_new = application.copy()
application_new['Result'] = application_new['ID'].isin(record['ID']).map({True: "核准", False: "拒絕"})

#分頁籤，第一頁是全部客戶概覽，第二頁是客戶資料查詢
tab1, tab2 = st.tabs(["申請客戶Portfolio", "客戶資料查詢"])
                           
with tab1:
    st.title('Apply Customer Portfolio')
    input_status = st.selectbox("審核狀態", ['全部','核准','拒絕'])
    if input_status == '全部':
        application_use = application_new
    else :
        application_use = application_new[application_new['Result'] == input_status]
    st.write('###### Raw Data')
    st.write(application)
    col1, col2, col3 = st.columns(3)

    with col1 :
        st.write('###### Distribution of Gender')
        GENDER_DF = application_use.groupby(['CODE_GENDER']).size().reset_index(name='CIF')
        st.bar_chart(
            GENDER_DF,
            x = 'CODE_GENDER',
            y = 'CIF'
        )

    #fig = go.Figure(
    #    go.Pie(
    #        labels = GENDER_DF['CODE_GENDER'],
    #        values= GENDER_DF['CIF'],
    #        hoverinfo = "label+percent",
    #        textinfo = "value"
    #
    #    )
    #)
    #st.plotly_chart(fig)
    #plt.pie(GENDER_DF['CIF'],labels = GENDER_DF['CODE_GENDER'])
    #plt.co
    #st.pyplot(plt)
    with col2 :
    #application.columns
        st.write('###### Distribution of Owning Car') 
        CAR_DF = application_use.groupby(['FLAG_OWN_CAR']).size().reset_index(name='CIF')
        st.bar_chart(
            CAR_DF,
            x = 'FLAG_OWN_CAR',
            y = 'CIF'
        )

    with col3 :
        st.write('###### Primary Income Type') 
        INCOME_TYPE_DF = application_use.groupby(['NAME_INCOME_TYPE']).size().reset_index(name='CIF').sort_values('CIF')
        st.bar_chart(
            INCOME_TYPE_DF,
            x = 'NAME_INCOME_TYPE',
            y = 'CIF'
        )

    st.write('###### Distribution of INCOME') 
    INCOME_DF = application_use[['AMT_INCOME_TOTAL','ID','OCCUPATION_TYPE']]

    st.scatter_chart(
        INCOME_DF,
        x = 'OCCUPATION_TYPE',
        y = 'AMT_INCOME_TOTAL',
        color = 'OCCUPATION_TYPE'
    )

    #紀錄轉換
    record_count = record.groupby('MONTHS_BALANCE')['STATUS'].value_counts().unstack(fill_value=0) #unstack：將行轉為列
    record_count.reset_index(inplace=True)
    record_count = record_count.sort_values(by=['MONTHS_BALANCE'])
    record_count = record_count.rename(columns={
        '0' : '逾期 1-29 天',
        '1' :'逾期 30-59 天',
        '2' : '逾期 60-89 天',
        '3' : '逾期 90-119 天',
        '4' : '逾期 120-149 天',
        '5' : '逾期或壞帳，超過 150 天核銷',
        'C' : '當月已還清',
        'X' : '當月無貸款'
    })
    record_count.columns.tolist()
    

    #for i in range(0,len(record_count)):
    #    if record_count['MONTHS_BALANCE'][i] == 0 :
    #        record_count['MONTHS_BALANCE'][i] = '當月'
    #    else :
    #        record_count['MONTHS_BALANCE'][i] = f"前{-record_count['MONTHS_BALANCE'][i]}月"
    #record_count
    st.write('###### Repayment Trends ') 
    if input_status == '拒絕':
        st.write('無還款紀錄')
    else :
        st.bar_chart(
            record_count,
            x = 'MONTHS_BALANCE',
            y = ['逾期 1-29 天', '逾期 30-59 天', '逾期 60-89 天', '逾期 90-119 天', '逾期 120-149 天', '逾期或壞帳，超過 150 天核銷', '當月已還清', '當月無貸款']
        )    

with tab2:
    st.title('Customer Information')
    #建篩選器
    input_id = int(st.selectbox("選擇查詢客戶ID", set(application['ID'])))
    filter_df = application[application['ID'] == input_id]
    #print(filter_df)
    #print(set(application['ID']))
    st.write(filter_df)
    col1, col2 = st.columns(2)
   

    if filter_df['ID'].isin(record['ID']).any():
        recordresult = '核准'
    else :
        recordresult = '拒絕'
    print(recordresult)

    
    st.write('### 審核結果:')
    st.write(recordresult)

    #紀錄轉換
    record_new2 = record.pivot(index = 'ID', columns = 'MONTHS_BALANCE', values = 'STATUS')
    #調整欄位名稱
    record_new2 = record_new2.rename(columns = lambda x: f"前{-x}月" if x < 0 else "本月")
    # 重置索引，確保 ID 是一個欄位
    record_new2.reset_index(inplace=True)
    
    st.write('###### Repayment Records') 
    st.write(record_new2[record_new2['ID'] == input_id])
