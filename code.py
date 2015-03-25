#!/usr/bin/env python
import web


urls = ('/','index',
        '/add','add',
        '/search', 'query',
        '/modify(.*?)','modify'
        
    #    the second value is the class which will be trigger
    # whe the url in the first value is called.
    
    

    )

app = web.application(urls, globals())
render = web.template.render('templates/')
db = web.database(dbn='mysql', user='root', pw='ca210946', db='test')

# I've declared it here so it can be acces from eery class.
# you just need to assigne a variable to it.



class index(object):
    def GET (self):

        return render.index()


class add:
    def GET(self):
        name = db.select('name')
        personalInfo = db.select('personalInfo')
        return render.add(name = name, personalInfo = personalInfo)
    def POST(self):
        u_input = web.input()
        
        namedb= db.insert('name', name = u_input.name, surname = u_input.surname,uuid = web.SQLLiteral("UUID()") )
        uuid = db.select('name',what='uuid',where = "name = '%s' AND surname = '%s'" %(u_input.name, u_input.surname))
        uuid_hash = uuid[0].uuid
        personalInfodb = db.insert('personalInfo', dir = u_input.dir, trabajo = u_input.trabajo, casa = u_input.casa, otro = u_input.otro, uuid= uuid_hash, empresa=u_input.empresa)
        saldosdb = db.insert('saldos',uuid= uuid_hash, fecha = web.SQLLiteral("NOW()"))
        id_person = db.select('personalInfo',what= "id", where="uuid = '%s'" % uuid_hash)
        update_name = db.update('name', where= "uuid = '%s'" % uuid_hash, id=id_person[0].id)

        raise web.seeother('/')
        
class query:
    def GET(self):
        try:
            u_input = web.input()
            q_field = u_input.field
            q_search = u_input.value
            
            if q_field in ("empresa","dir"):
                personalInfo_forSearch = db.select('personalInfo', where= " %s  = '%s' ;" % (q_field, q_search))
                personalInfo_id = db.select('personalInfo', what="id" ,where=" %s  = '%s' ;" % (q_field, q_search))
                number = []
                
                
                for user in personalInfo_id:
                    
                    number.append(int(user.id))
                    number.append(0)
                
                # try reparam()
                number_tuple= tuple(number)
                number_tuple = str(number_tuple)
                name_forSearch= db.select('name', where="id IN %s" % number_tuple )
                
                return render.search(name=  name_forSearch, personalInfo= personalInfo_forSearch)
            elif q_field in ("name","surname"):
                name_forSearch= db.select('name', where="%s = '%s' ;" % (q_field,q_search) )
                name_uuid = db.select('name', what="uuid", where="%s = '%s' ;" % (q_field,q_search))
                
               
                number = []
                
                
                for user in name_uuid:
                    uuid_hash = user.uuid
                   
                    number.append(str(uuid_hash))
                    number.append(0)
                
                # try reparam()
                number_tuple= tuple(number)
                number_tuple = str(number_tuple)
                personalInfo_forSearch = db.select('personalInfo', where= " uuid IN %s ;" % number_tuple)
                return render.search(name=  name_forSearch, personalInfo= personalInfo_forSearch)

            else:
                personalInfo_forSearch = db.select('personalInfo', where= " %s  = %s ;" % (q_field, q_search))
                personalInfo_id = db.select('personalInfo',what="id",where=" %s  = %s ;" % (q_field, q_search))
                number = []


                for user in personalInfo_id:

                    number.append(int(user.id))
                    number.append(0)


                number_tuple= tuple(number)
                number_tuple = str(number_tuple)
                name_forSearch = db.select('name', where="id IN %s" % number_tuple)
                return render.search(name=  name_forSearch, personalInfo= personalInfo_forSearch)     
        except Exception, e:    
                
            return render.search(name=db.select('name',where="id=0"), personalInfo = db.select("personalInfo",where="id=0"))
        
        
     
    def POST(self):
      
        u_input = web.input()   
        q_search =u_input.to_search
        q_field = u_input.field
       
        raise web.seeother('/search?value=%s&field=%s' % (q_search, q_field))

   

class modify:
    def GET(self):
        u_input= web.input()
        user_id = u_input.id
        modify_query = db.query("SELECT * FROM name JOIN saldos WHERE name.id = %s AND saldos.id = %s " %(user_id,user_id))
        
        return render.modify(query = modify_query)

   
    def POST(self):
        u_input = web.input()
        U_detalle = u_input.detalle
        u_debe = u_input.debe
        u_haber = u_input.haber
        u_id = u_input.id
        send_modification = db.update('saldos',where="id = %s" % u_id , detalle = U_detalle, debe= u_debe, haber = u_haber, fecha =web.SQLLiteral("NOW()"))
        raise web.seeother('/search')

if __name__ == '__main__':
    app.run()
