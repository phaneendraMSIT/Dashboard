import MySQLdb as sql
import pandas as pd
import plotly
import plotly.graph_objs as go


def connectServer():
    connect = sql.connect( host="localhost", user="root", passwd="1234" )
    return connect


sqlCursor = connectServer().cursor()


def getItemPieChart(dataFrame):
    fig = go.Figure( {
        "data": [go.Pie( labels=dataFrame['ItemName'].tolist(), values=dataFrame["Amount"].tolist(), hole=.75 )],
        "layout": go.Layout( margin={"l": 30, "r": 0, "b": 30, "t": 0}, legend={"x": 1, "y": 0.7} )
    } )
    return fig


def convertVolume(totalVolume):
    stringVolume = ""
    if totalVolume >= 1000:
        stringVolume = str( totalVolume / 1000 ) + " Tones"
    else:
        stringVolume = str( totalVolume ) + " Kgs"
    return stringVolume


def getCities(userId):
    sqlCursor.execute( "select loc.name from stakeholders.jhi_user ju "
                       "left join stakeholders.customer cus on ju.id = cus.user_id "
                       "left join recykal.location loc on cus.id = loc.customer_id "
                       "where  ju.id = " + userId + " ;" )
    city = sqlCursor.fetchall()
    cityList = [list( c )[0] for c in city]

    return cityList


def getInwardValue(userId, location, startDate, endDate):
    sqlCursor.execute(
        "select sum(po.total_amount) ,sum(po.total_qty)  from recykal.pickup_order po "
        "left join recykal.location l on po.to_location_id = l.id "
        "where po.buyer_user_id = " + userId + " and po.status = 'ORDER_COMPLETED' "
                                               "and l.name = '" + location + "'and  po.created_date BETWEEN '" + startDate + "' and '" + endDate + "'+interval 1 day"
    )

    result_1 = sqlCursor.fetchall()
    # if result_1[0][0] is None:
    #     return 0, 0,  go.Figure({'data': [], 'layout': {}})

    totalAmount = int( result_1[0][0] )
    totalVolume = int( result_1[0][1] )

    totalVolume = convertVolume( totalVolume )

    sqlCursor.execute( "select i.name itemName, sum(oi.received_qty) Amount, i.default_unit_id unit from "
                       "recykal.pickup_order po "
                       "left join recykal.order_item oi on po.id = oi.pickup_order_id "
                       "left join recykal.item i on oi.item_id = i.id "
                       "left join recykal.location loc on po.to_location_id = loc.id "
                       "where po.status = 'ORDER_COMPLETED' and  po.buyer_user_id = " + userId + " and loc.name = '" + location + "' and po.created_date BETWEEN '" + startDate + "' and '" + endDate + "'+interval 1 day group by oi.item_name order by Amount desc limit 5" )

    rows = sqlCursor.fetchall()
    items = pd.DataFrame( [ij for ij in i] for i in rows )
    items.rename( columns={0: 'ItemName', 1: 'Amount', 2: 'Unit'}, inplace=True )
    items['Amount'] = [int( i ) for i in items['Amount']]
    fig = getItemPieChart( items )

    return "Rs " + str( totalAmount ), totalVolume, fig


def getOutwardValue(userId, location, startDate, endDate):
    sqlCursor.execute( "select sum(po.total_amount) ,sum(po.total_qty)  from recykal.pickup_order po "
                       "left join recykal.location l on po.from_location_id = l.id "
                       "where po.seller_user_id = " + userId + " and po.status = 'ORDER_COMPLETED' and l.name = '" + location + "' and  po.created_date BETWEEN '" + startDate + "' and '" + endDate + "'+interval 1 day" )

    result = sqlCursor.fetchall()

    # if result[0][0] is None:
    #     return 0, 0,  go.Figure({'data': [], 'layout': {}})
    totalAmount = int( result[0][0] )
    totalVolume = int( result[0][1] )

    totalVolume = convertVolume( totalVolume )

    sqlCursor.execute(
        "select i.name itemName, sum(oi.received_qty) Amount, i.default_unit_id unit from recykal.pickup_order po "
        "left join recykal.order_item oi on po.id = oi.pickup_order_id "
        "left join recykal.item i on oi.item_id = i.id "
        "left join recykal.location loc on po.from_location_id = loc.id"
        " where po.status = 'ORDER_COMPLETED' and  po.seller_user_id =" + userId + " and loc.name = '" + location + "' and po.created_date BETWEEN '" + startDate + "' and '" + endDate + "'+interval 1 day group by oi.item_name order by Amount desc limit 5;" )
    rows = sqlCursor.fetchall()
    items = pd.DataFrame( [ij for ij in i] for i in rows )
    items.rename( columns={0: 'ItemName', 1: 'Amount', 2: 'Unit'}, inplace=True )
    items['Amount'] = [int( i ) for i in items['Amount']]

    fig = getItemPieChart( items )

    return "Rs " + str( totalAmount ), totalVolume, fig


# print( getCities( '146780' ) )
