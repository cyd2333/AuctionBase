#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = ('/currtime', 'curr_time',
        '/selecttime', 'select_time',
        '/search', 'search',
        '/item','item',
        '/add_bid','add_bid',
        # TODO: add additional URLs here
        # first parameter => URL, second parameter => class name
        )
###add_bid
class add_bid:
    # A simple GET request, to '/addbid'
    #
    # Notice that we pass in `add_bid' to our `render_template' call
    # in order to have its value displayed on the web page
    
    def GET(self):
        current_time = sqlitedb.getTime()
        add_result = True
        return render_template('add_bid.html')  
        # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests

    def POST(self):
        #transaction and test 
        t = sqlitedb.transaction()
        try:
            post_params = web.input()
            item_id = int(post_params['itemID'])
            user_id = post_params['userID']
            price = float(post_params['price'])
            current_time = sqlitedb.getTime()
            started = sqlitedb.query("select Started from Items where ItemID = $item_id", {'item_id': item_id})
            ends = sqlitedb.query("select Ends from Items where ItemID = $item_id", {'item_id': item_id})
            buyPrice = sqlitedb.query("select Buy_Price from Items where ItemID = $item_id", {'item_id': item_id})[0].Buy_Price
            #current_price =  sqlitedb.query("select Currently from Items where ItemID = $item_id", {'item_id': item_id})[0].Currently
            if(buyPrice != None):
                closed = sqlitedb.query("select * from Bids where (ItemID = $item_id) and (Amount >= $buyPrice)",{'item_id': item_id, 'buyPrice': buyPrice})
            else:
                closed = None
            if (closed is None): 
                #add bid to the database
                sqlitedb.updateTime("insert into Bids values ($item_id, $user_id, $price, $currTime)",{'item_id':item_id,'user_id':user_id,'price':price,'currTime':current_time})
                sqlitedb.updateTime("update Items set Currently = $currently where ItemID = $item_id",{'currently':price, 'item_id':item_id})
                
                add_result = "done"
                update_message = 'Hello, %s. Previously added a bid for %d. of price $%d.'% (user_id, item_id, price)
            else:
                update_message = "Failed. Try again."
                add_result = ""
            
        except Exception as e:
            t.rollback()
            print str(e)
            add_result = ""
            update_message = "Failed. Try again."
        else:
            t.commit()    
        return render_template('add_bid.html',message = update_message, add_result = add_result)

class item:
    def GET(self):
        
        data = web.input()
        itemID = int(data.itemID)
#        return render_template('item.html', itemID = itemID
        item = sqlitedb.query('select distinct * from Items where ItemID = $ID',{'ID': itemID})
        cate = sqlitedb.query('select Category from Categories where ItemID = $ID', {'ID': itemID})
        start = sqlitedb.query('select distinct Started from Items where ItemID = $ID',{'ID': itemID})
        end = sqlitedb.query('select distinct Ends from Items where ItemID = $ID',{'ID': itemID})
        buyprice = sqlitedb.query('select distinct Buy_Price from Items where ItemID = $ID',{'ID': itemID})
        cur = sqlitedb.query('select Currently from Items where ItemID = $ID',{'ID': itemID})
        count = 0
        
        cur_time = string_to_time(sqlitedb.getTime())
        start = string_to_time(start[0]['Started'])
        end = string_to_time(end[0]['Ends'])
        print "****"
        print cur_time
        print start
        print end
        print buyprice
        if(cur_time > start and cur_time > end):
            status = "CLOSE"
        if(cur_time > start and cur_time < end):
            status = "OPEN"
        if(cur_time < start and cur_time < end):
            status = "NOT START"
        if(buyprice[0]['Buy_Price'] != None):
            if(cur >= buyprice):
                status = "CLOSE"
        print status
        print "****"
        winner = ""
        auction = sqlitedb.query('select UserID, Amount, Time from Bids where ItemID = $ID', {'ID': itemID})
        if(status == "CLOSE"):
            winner = sqlitedb.query('select UserID from Bids where ItemID = $ID order by Amount DESC LIMIT 1', {'ID': itemID})
            print winner
            if(winner):
                winner = (winner[0]['UserID'])
        return render_template('item.html', item_result = item, category_result = cate, status_result = status, auction_result = auction, winner_result = winner)
class search:
    def GET(self):
        return render_template('search.html')
    def POST(SELF):
        post_params = web.input()
        item_id = post_params['itemID']
        user_id = post_params['userID']
        min_price = post_params['minPrice']
        max_price = post_params['maxPrice']
        category = post_params['category']
        status = post_params['status']
        description = post_params['description']
        line1 =""
        line2 =""
        line3 =""
        line4 =""
        line5 =""
        line6 =""
        line7 =""
        Item_id = ""
        userId = ""
        minPrice = ""
        maxPrce = ""
        
    
        #grab current time
        current_time = sqlitedb.getTime()
        print current_time
        #do some query based on the input
        try:
            if(item_id != ""):
                Item_id = int(item_id)
                line1="(select ItemID from Items where ItemID = $Item_id) "
            if(user_id != ""):
                userId = user_id
                line2= "(select ItemID from Items where Seller_UserID = $userId) "
            if(min_price != ""):
                minPrice = float(min_price)
                line3 = "(select ItemID from Items where Currently >= $minPrice) "
            if(max_price != ""):
                maxPrce = float(max_price)
                line4 = "(select ItemID from Items where Currently <= $maxPrice) "
            if(category != ""):
                line5 = "(select ItemID from Categories where Category = $category)"
        except Exception as e:
            message = "please write valid input!"
            return render_template('search.html',message = message)
        if(status == "open"):
            line6 = "(select ItemID from Items where (Started <= $current_time) and (Ends >= $current_time) or Currently > Buy_Price)"
        if(status == "all"):
            line6 = "(select ItemID from Items)"
        if(status == "close"):
            line6 = "(select ItemID from Items where (Started < $current_time) and (Ends < $current_time))"
        if(status == "notStarted"):
            line6 = "(select ItemID from Items where (Started > $current_time) and (Ends > $current_time))"
        if(description != ""):
            line7 = "(select ItemID from Items where instr(Description, $description) > 0)"
        
        res = [line1, line2, line3, line4, line5, line6,line7]
        query_string = "select distinct * from Items inner join Categories on Items.ItemID = Categories.ItemID where Items.ItemID in "
        isFirst = False
        for i in range(len(res)):
            if isFirst == False and res[i] != "":
                isFirst = True
                query_string += res[i]
            elif res[i] != "":
                query_string += "and Items.ItemID in "
                query_string += res[i]
        query_string += " group by Items.ItemID"
        result = sqlitedb.query(query_string, {'Item_id':Item_id, 'userId':userId,'minPrice':minPrice, 'maxPrice':maxPrce, 'category':category, 'current_time':current_time, 'description':description})
        #check status
        count = 0
        status = range(len(result))
        itemID = range(len(result))
        counter = 0
        cur_time = string_to_time(sqlitedb.getTime())
        for a in result:
            for b in a:
                count += 1
                if(count%11 == 1):
                    itemID[counter] = int(a[b])
                if(count%11 == 6):
                    start = string_to_time(a[b])
                if(count%11 == 3):
                    end = string_to_time(a[b])
                if(count%11 == 8):
                    cur = int(a[b])
                if(count %11 == 9):
                    buyprice = a[b]
            if(cur_time > start and cur_time > end):
                status[counter] = "CLOSE"
            if(buyprice != None):
                buy = int(buyprice)
                if(cur >= buy):
                    status[counter] = "CLOSE"
            if(cur_time > start and cur_time < end):
                status[counter] = "OPEN"
            if(cur_time < start and cur_time < end):
                status[counter] = "NOT START"
            count = 0
            counter += 1
    
    
        return render_template('search.html',search_result =result, status = status, itemID = itemID)
    
class curr_time:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        current_time = sqlitedb.getTime()
        return render_template('curr_time.html', time = current_time)

class select_time:
    # Aanother GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html')

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss'];
        enter_name = post_params['entername']


        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time)
        # TODO: save the selected time as the current time in the database3
        t = sqlitedb.transaction()
        try:
            sqlitedb.updateTime('update CurrentTime set Time = $time', {'time': selected_time})
        except Exception as e:
            message = "you are not allowed to select time previous!"
            return render_template('select_time.html', message = message)
        else:
            t.commit()
        #sqlitedb.updateTime(selected_time)
        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        return render_template('select_time.html', message = update_message)

###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
