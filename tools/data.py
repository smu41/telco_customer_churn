import numpy as np
import pandas as pd

# Read data
def load_data() -> pd.DataFrame:
    data = pd.read_csv('../data/telco.csv')
    data.columns = data.columns.str.strip().str.lower().str.replace(r'\s+', '_', regex=True)
    data['churn_value'] = data['churn_label'].values.map({'Yes': 1, 'No': 0})

    bins = [0, 24, 34, 44, 54, 64, 120]
    labels = ['<25', '25-34', '35-44', '45-54', '55-64', '65+']
    data['age_band'] = pd.cut(data['age'], bins=bins, labels=labels)

    bins_life = [-1, 3, 12, 24, 48, 120]
    labels_life = ['0-3', '4-12', '13-24', '25-48', '49+']
    data['tenure_band'] = pd.cut(data['tenure_in_months'], bins_life, labels=labels_life)

    return data

data = load_data()

def metrics(data) -> pd.DataFrame:
    total_c = data.shape[0]
    stayed_c = data.loc[data['customer_status'] == 'Stayed'].shape[0]
    churn_c = data.loc[data['customer_status'] == 'Churned'].shape[0]
    churn_rate = float(churn_c / total_c) * 100
    retention_rate = float(data.loc[data['churn_value'] == 0].shape[0] / total_c) * 100
    revenue = data['total_revenue'].sum()
    churn_revenue = data.loc[data['churn_value'] == 1, 'total_revenue'].sum()
    monthly_risk_revenue = data.loc[data['churn_value'] == 1, 'monthly_charge'].sum()
    churn_cltv_risk = data.loc[data['churn_value'] == 1, 'cltv'].mean()

    metric_dict = {'total_customers': total_c,
                   'stayed_customers': stayed_c,
                   'churn_customers': churn_c,
                   'churn_rate': churn_rate,
                   'retention_rate': retention_rate,
                   'risk_cltv': churn_cltv_risk,
                   'total_revenue': revenue,
                   'churn_revenue': churn_revenue,
                   'monthly_risk_revenue': monthly_risk_revenue}
    metric = pd.DataFrame(metric_dict, index=[0])

    return metric

def status_c(data) -> pd.DataFrame:
    status = data.groupby('customer_status')['customer_id'].count().reset_index()
    return status

def age_churn(data) -> pd.DataFrame:
    churn_age = data.loc[data['churn_value'] == 1, 'age_band'].value_counts()
    age_c = data['age_band'].value_counts()
    age_churn_c = pd.concat([churn_age, age_c], axis=1).reset_index()
    age_churn_c.columns = ['age_band', 'churned', 'customer']

    return age_churn_c

def revenue_contract(data) -> pd.DataFrame:
    contract = data.groupby('contract')['total_revenue'].sum()
    churn_contract_rev = data.loc[data['churn_value'] == 1,
    ['contract', 'total_revenue']].groupby('contract')['total_revenue'].sum()
    revenue = pd.concat([churn_contract_rev, contract], axis=1).reset_index()
    revenue.columns = ['contract', 'churn_revenue', 'total_revenue']

    return revenue

def city_revenue(data) -> pd.DataFrame:
    c_revenue = data.groupby('city').agg(total_revenue=('total_revenue', 'sum'),
                                            count=('total_revenue', 'count'),
                                            churned=('churn_value', 'mean'),
                                            lat=('latitude', 'mean'),
                                            lon=('longitude', 'mean')).sort_values(by='total_revenue',
                                                                                   ascending=False).reset_index()

    c_revenue['rank'] = c_revenue['count'].rank(ascending=False)

    # 計算size大小
    min_marker_size = 5
    max_marker_size = 23

    customer_min = c_revenue['count'].min()
    customer_max = c_revenue['count'].max()

    c_revenue['marker_size'] = (
            min_marker_size
            + (c_revenue['count'] - customer_min)
            / (customer_max - customer_min)
            * (max_marker_size - min_marker_size))

    return c_revenue

def churn_reason(data) -> pd.DataFrame:
    reason = data.loc[data['churn_value'] == 1, 'churn_reason'].value_counts().head(12).reset_index()
    reason['cum_pct'] = reason['count'].cumsum() / reason['count'].sum()

    return reason

def churned_pie(data) -> pd.DataFrame:
    churned = data.groupby('churn_label')['customer_id'].count().reset_index()
    return churned

def pay_method(data) -> pd.DataFrame:
    payment = data.groupby('payment_method').agg(customer_id=('customer_id', 'size'),
                                                 churn_value=('churn_value', 'sum'))

    joined = data.loc[data['customer_status'] == 'Joined', 'payment_method'].value_counts()
    pay_joined = pd.concat([joined, payment], axis=1).reset_index()
    pay_joined.columns = ['payment_method', 'joined', 'customer_id', 'churn_value']

    pay_joined['stayed_rate'] = (pay_joined['customer_id'] -
                                 pay_joined['joined'] -
                                 pay_joined['churn_value']) / pay_joined['customer_id'] * 100
    pay_joined['churn_rate'] = pay_joined['churn_value'] / pay_joined['customer_id'] * 100

    return pay_joined

def q_retention(data) -> pd.DataFrame:
    data['risk_score'] = data['churn_score']
    data['value_score'] = data['cltv']
    data['sat_score'] = data['satisfaction_score']

    risk_th = np.nanpercentile(data['risk_score'], 70) if np.isfinite(data['risk_score']).any() else np.nan
    value_th = np.nanpercentile(data['value_score'], 70) if np.isfinite(data['value_score']).any() else np.nan

    data['risk_flag'] = np.where(np.isnan(data['risk_score']), 0, (data['risk_score'] >= risk_th))
    data['value_flag'] =np.where(np.isnan(data['value_score']), 0, (data['value_score'] >= value_th))
    data['low_sat_flag'] = np.where(np.isnan(data['sat_score']), 0, (data['sat_score'] <= 2))
    data['retention_quadrant'] = np.select([(data['risk_flag'] == 1) & (data['value_flag'] == 1) & (data['low_sat_flag'] == 1),
                                            (data['risk_flag'] == 1) & (data['value_flag'] == 1),
                                            (data['risk_flag'] == 1) & (data['value_flag'] == 0),
                                            (data['risk_flag'] == 0) & (data['value_flag'] == 1)],
                                           ['High Risk x High Value x High Satisfaction',
                                            'High Risk x High Value',
                                            'High Risk x Low Value',
                                            'Low Risk x High Value'], default=['Low Risk x Low Value'])

    quadrant = data['retention_quadrant'].value_counts().rename('retention_quadrant').reset_index(name='customers')
    quadrant['share'] = quadrant['customers'] / quadrant['customers'].sum()
    quadrant['share_pct'] = quadrant['share'] * 100

    return quadrant, data

def risk_c(data) -> pd.DataFrame:
    c_risk = data.loc[data['churn_value'] == 1]
    c_risk['monthly_revenue'] = c_risk['total_revenue'] / c_risk['tenure_in_months']
    c_risk = c_risk.sort_values(by=['monthly_revenue'], ascending=False).reset_index(drop=True)
    c_risk['rank'] = c_risk.index + 1

    return c_risk

def city_risk(data) -> pd.DataFrame:
    data['rev_at_risk'] = data['churn_value'] * data['monthly_charge']
    data['monthly_rev_at_risk'] = data['total_revenue'] / data['tenure_in_months']

    rev_at_risk = (data.query('churn_value == 1 & monthly_charge >= 101.3')
                   .groupby('city')
                   .agg(monthly_revenue=('monthly_rev_at_risk', 'sum'),
                        lat=('latitude', 'mean'),
                        lon=('longitude', 'mean'),
                        customer=('customer_id', 'count')).reset_index())

    # 設置size大小
    # 讓數量大的城市呈現較大紅點，
    # 同時避免最大值太誇張。
    min_marker_size = 5
    max_marker_size = 23

    customer_min = rev_at_risk['customer'].min()
    customer_max = rev_at_risk['customer'].max()

    rev_at_risk['marker_size'] = (
            min_marker_size
            + (rev_at_risk['customer'] - customer_min)
            / (customer_max - customer_min)
            * (max_marker_size - min_marker_size))

    return rev_at_risk

def churn_category(data) -> pd.DataFrame:
    cate = data.loc[data['churn_value'] == 1, 'churn_category'].value_counts().reset_index(name='customers')

    return cate

def lifecycle(data) -> pd.DataFrame:
    data = data.loc[data['churn_value'] == 1]
    tb = data.groupby(['tenure_band', 'churn_category'],
                      observed=True).agg(customers=('churn_value', 'size')).reset_index()

    reason = data.groupby(['churn_category', 'churn_reason'],
                          observed=True).agg(customers=('churn_value', 'size')).reset_index()
    reason['share'] = reason['customers'] / reason['customers'].sum() * 100

    return tb, reason

def con_life(data) -> pd.DataFrame:
    tract_life = data.groupby(['tenure_band', 'contract'],
                              observed=True).agg(churned=('churn_value', 'sum'),
                                                 churn_rate=('churn_value', 'mean')).reset_index()
    return tract_life

def concentra(data) -> pd.DataFrame:
    concen = (data.groupby('tenure_band', observed=True)
              .agg(churned=('churn_value', 'mean'),
                   customers=('churn_value', 'size'))
              .sort_values('customers', ascending=False)
              .reset_index())
    concen['rank'] = concen['customers'].rank(ascending=False)
    return concen

def churn_city(data) -> pd.DataFrame:
    c_churn = (data.groupby('city', observed=True)
               .agg(churned=('churn_value', 'mean'),
                    customers=('churn_value', 'size'),
                    lat=('latitude', 'mean'),
                    lon=('longitude', 'mean'))
               .sort_values('customers', ascending=False).reset_index())

    min_marker_size = 5
    max_marker_size = 23

    customer_min = c_churn['customers'].min()
    customer_max = c_churn['customers'].max()

    c_churn['marker_size'] = (
            min_marker_size
            + (c_churn['customers'] - customer_min)
            / (customer_max - customer_min)
            * (max_marker_size - min_marker_size))

    c_churn['rank'] = c_churn['customers'].rank(ascending=False)
    return c_churn

if __name__ == '__main__':
    met = city_revenue(data)
    print(met.loc[met['count'] > 10])
