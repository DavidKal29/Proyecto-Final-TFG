from models.entities.Product import Product


class ModelProduct():

    #Función basica para mostrar productos en inicio
    @classmethod
    def mostrar_productos(cls,db,order):
        try:
            #Se abre un cursor con la conexion a la db y se crea la consulta sql
            cursor=db.connection.cursor()

            #En este caso, en home, se mostrarán productos mas venidos y 
            # mas nuevos por tanto, la variable order tendrá id o
            # ventas, para poder filtrar y sacar los productos requeridos
            if order=='id':
                sql='SELECT id,nombre,precio,imagen FROM productos WHERE activo=1 ORDER BY id DESC LIMIT 8'
            elif order=='ventas':
                sql='SELECT id,nombre,precio,imagen FROM productos WHERE activo=1 ORDER BY ventas DESC LIMIT 8'
            else:
                cursor.close()
                return None

            #Ejecutamos la consulta
            cursor.execute(sql)
            resultados=cursor.fetchall()
           
            #Si la consulta devuelve datos, creamos una lista, recorremos los datos 
            # y creamos un objeto con cada producto, metiendolos en la lista
            if resultados:
                productos=[]

                for resultado in resultados:
                    id=resultado[0]
                    nombre=resultado[1]
                    precio=resultado[2]
                    imagen=resultado[3]

                    productos.append(Product(id,nombre, precio, None, None, None, imagen))

                cursor.close()
                return productos
                
            #Si no hay resultados, retornamos None    
            else:
                cursor.close()
                return None
        
        
        #Si hay errores, devolvemos None tambien
        except Exception as error:
            print(error)
            return None
        
        

    #Función basica para mostrar productos en inicio
    @classmethod
    def mostrar_favoritos(cls,db,id_usuario):
        try:
            #Se abre un cursor con la conexion a la db y se crea la consulta sql
            cursor=db.connection.cursor()

            #Montamos la consulta para obtener los favortios(maximo 12 favoritos)
            sql='''
                SELECT p.id,p.nombre,p.precio,p.imagen FROM productos p
                INNER JOIN favoritos f
                ON p.id=f.id_producto
                WHERE f.id_usuario=%s
                ORDER BY f.id DESC
                LIMIT 12
            ''' 

            #Ejecutamos la consulta
            cursor.execute(sql,(id_usuario,))
            resultados=cursor.fetchall()
           
            #Si la consulta devuelve datos, creamos una lista, recorremos los datos 
            # y creamos un objeto con cada producto, metiendolos en la lista
            if resultados:
                productos=[]

                for resultado in resultados:
                    id=resultado[0]
                    nombre=resultado[1]
                    precio=resultado[2]
                    imagen=resultado[3]

                    productos.append(Product(id,nombre, precio, None, None, None, imagen))

                cursor.close()
                return productos
                
            #Si no hay resultados, retornamos None    
            else:
                cursor.close()
                return None
        
        
        #Si hay errores, devolvemos None tambien
        except Exception as error:
            print(error)
            return None
        

    #Metodo para ver si un producto está en la lista de favoritos de un usuario
    @classmethod
    def checkFavorite(cls,db,id_usuario,id_producto):
        try:
            #Se abre un cursor con la conexion a la db y se crea la consulta sql
            cursor=db.connection.cursor()

            #Vemos a ver si ese producto ya está en favoritos
            sql='SELECT id_producto FROM favoritos WHERE id_producto=%s and id_usuario=%s'
            cursor.execute(sql,(id_producto,id_usuario))

            existe=cursor.fetchone()

            #Si el producto existe en favoritos, retornamos true
            if existe and existe[0]:
                cursor.close()
                return True
            
            #Sino None
            else:
                cursor.close()
                return None

           
        #Si hay errores, devolvemos None tambien
        except Exception as error:
            print(error)
            return None
        
        
    #Metodo para añadir a favoritos
    @classmethod
    def addFavorites(cls,db,id_usuario,id_producto):
        try:
            #Se abre un cursor con la conexion a la db y se crea la consulta sql
            cursor=db.connection.cursor()

            existe=cls.checkFavorite(db,id_usuario,id_producto)

            #Vemos si el producto está activo y si no es asi no dejamos añadirlo
            sql='SELECT activo FROM productos WHERE id=%s'
            cursor.execute(sql,(id_producto,))

            resultado=cursor.fetchone()

            if resultado and resultado[0]:
                activo=resultado[0]

                if activo==0:
                    cursor.close()
                    return None
            
            else:
                cursor.close()
                return None

            #Si el producto existe en favoritos, no dejamos añadirlo
            if existe:
                cursor.close()
                return 'El producto ya está en tu lista de favoritos'

            #Obtenemos la cantidad de favoritos de un usuario
            sql='SELECT COUNT(*) FROM favoritos WHERE id_usuario=%s'
            cursor.execute(sql,(id_usuario,))

            cantidad=cursor.fetchone()

            #Si la cantidad es mayor o igual a 12 no permitimos añadir más
            if cantidad and cantidad[0]>=12:
                cursor.close()
                return 'Solo puedes tener 12 productos en favoritos'
            
          
            #Insertamos en la tabla favoritos, los ids del producto y usuario
            sql='INSERT INTO favoritos (id_usuario,id_producto) VALUES (%s,%s)'
            cursor.execute(sql,(id_usuario,id_producto))
            db.connection.commit()

            cursor.close()

            return True

           
        #Si hay errores, devolvemos None tambien
        except Exception as error:
            print(error)
            return None
        

    #Metodo para borrar favoritos de la lista
    @classmethod
    def deleteFavorites(cls,db,id_usuario,id_producto):
        try:
            #Se abre un cursor con la conexion a la db y se crea la consulta sql
            cursor=db.connection.cursor()

            #Borramos el producto(si no existe da igual, no se borra y ya)
            sql='DELETE FROM favoritos WHERE id_producto=%s and id_usuario=%s'
            cursor.execute(sql,(id_producto,id_usuario))
            db.connection.commit()

            cursor.close()

            return True

           
        #Si hay errores, devolvemos None tambien
        except Exception as error:
            print(error)
            cursor.close()
            return None


    
    #Metodo estatico para convertir la busqueda que es un string, 
    # en una lista de terminos para filtrar en la consulta
    @staticmethod
    def procesar_search(search,categorias):
        import unidecode

        #Quitar espacios, hacer todo en minusculas y quitar tildes
        search=search.strip()
        search=search.lower()
        search=' '.join(search.split())
        search=unidecode.unidecode(search)

        #Dividiremos el search en palabras que usaremos para 
        # buscar el nombre del producto utilizando likes
        terminos=search.split()

       
        for i in range(len(terminos)):
            
            #Si la palabra kilo no esta junto al numero (20 kilos o 20 kg)
            if ('kilo' in terminos[i] or 'kg' in terminos[i]) and terminos[i].isalpha():
                terminos[i]='kg'

            
            #Si la palabra kilo y el numero estan juntos (20kilos o 20kg) 
            if ('kilo' in terminos[i] or 'kg' in terminos[i]) and not terminos[i].isalpha() and not terminos[i].isdigit():
                
                #Vamos recorriendo el termino, metiendo en 
                # una lista los numeros que saquemos de ahi
                numeros=[]
                numero=''
                
                #Recorremos los terminos
                for p in terminos[i]:

                    #Si el p es un numero o un punto, concatenamos a numero
                    if p.isdigit() or p=='.':
                        numero+=p

                    #Sino, nos hemos encontrado una letra, añadimos a la lista de numeros el numero
                    else:
                        numeros.append(numero)
                        numero=''
                
                #Appendeamos el ultimo numero
                numeros.append(numero)

                #Añadimos a los terminos todos los numeros
                for n in numeros:
                    terminos.append(n)

                #Hacemos que el termino se vuelva '', luego sera filtrado  
                terminos[i]=''


        #Reemplazamos las comas por puntos, para los floats
        terminos[i]=terminos[i].replace(',','.')
                
        #Comprobamos si un termino es un float o no
        for i in range(len(terminos)):
            try:
                valor=float(terminos[i])
                print(valor)
            
            except:
                #Si no es un float, tiene letras
                print('No es un float')
                
                #Si no es un alfanumerico, quiere decir que tiene caracteres raros
                if not terminos[i].isalnum():
                    print('Contiene terminos raros')

                    #Creamo una lista solo con caracteres normales y los juntamos con join
                    terminos[i]=''.join([p for p in terminos[i] if p.isalnum()])

                #Con esto, evitamos palabras tipo d#isco o cosas raras


        #Terminos que podrian escribirse mal y no se rencontrado
        reglas={
            'rodilleras':['rodill'],
            'coderas':['cod'],
            'estructura':['maquina'],
            'gorilla':['gorila'],
            'inclinado':['inclinado'],
            'plano':['plano'],
            'banco':['banca'],
            'agarre':['agarre', 'ganch', 'agarra'],
            'banda':['liga','elastic'],
            'topes':['tope','cierre','seguro','seguridad'],
            'mancuerna':['pesa','mancu'],
            'kettlebell':['ruso', 'rusa','ketlebel']
        }

       
        #Recorremos todos los terminos
        for i in range(len(terminos)):
            #Recorremos el dicionario de reglas
            for nuevo_valor, patrones in reglas.items():
                #Recorremos la lista de cada clave
                for patron in patrones:
                    #Si el patron esta dentro de un termino sustituimos
                    if patron in terminos[i]:
                        terminos[i]=nuevo_valor
                        break  
                
            
        #Aprovechamos las categorias para poner en singular lo que se busca      
        for i in range(len(terminos)):              
            for categoria in categorias:
                if terminos[i]==categoria.nombre.lower():
                    terminos[i]=categoria.nombre.lower()[:-1]


        
        #Si hay palabras inutiles que molestan a la hora de filtrar, las borramos
        for i in range(len(terminos)-1,-1,-1):
            if terminos[i] in ['','de','o','en','la','el','los','las','y','a','para','por','con','un','una','unos','unas']:
                del terminos[i]
     

        #Variable para ver si hay numeros o decimales
        hay_numeros=False
        

        #Recorrer los terminos, ver si es numero/decimal, 
        # y poner True la variable si es asi
        for i in range(len(terminos)):
            if terminos[i].isdigit():
                hay_numeros=True
                print('Es un digito')
            else:
                try:
                    termino_float=float(terminos[i])
                    print('Es un float')
                    hay_numeros=True
                except:
                    print('No es un numero')

        
        #Si hay numeros, borramos todos los terminos que sean kg, 
        # para evitar que al hacer la consulta, pille todos los 
        # productos que tengan kg en el nombre
        if hay_numeros:
            for i in range(len(terminos)-1,-1,-1):
                if terminos[i]=='kg':
                    del terminos[i]

        
        print('Los terminos:',terminos)
                
        return terminos
    
    
    
        
    #Metodo para construir el where de la consulta para mostrar los productos
    @classmethod
    def construir_where(cls,parametros,categorias,admin=False):
        
        #Creamos la lista donde van las condiciones del where y 
        # la usaré para luego juntar todo con un join
        condiciones=[]

        #Si hay parametros va mirando cada posible parametro, y añade 
        # a la lista un string que se juntará con el join
        if parametros:

            if 'marca' in parametros:
                condiciones.append("p.id_marca={}".format(parametros['marca']))


            if 'categoria' in parametros:
                condiciones.append("p.id_categoria={}".format(parametros['categoria']))


            if 'precio' in parametros:

                #Divide el stirng por el precio minimo y maximo
                rangos=parametros['precio'].split('-')
                precio_min=rangos[0]
                precio_max=rangos[1]

                condiciones.append("p.precio>={} AND p.precio<={}".format(precio_min,precio_max))


            #Si alguien buscó algo en el buscador
            if 'search' in parametros:
    
                #Obtiene una lista de eso que buscó usando el metodo estatico para procesar el search
                terminos=cls.procesar_search(parametros['search'],categorias)

                #Creamos listas para los tipos de condiciones
                condiciones_palabras=[]
                condiciones_numeros=[]
                condiciones_marcas=[]
                condiciones_materiales=[]
                condiciones_kilos=[]


                #Recorre los terminos
                for termino in terminos:
                    #Si es un número, añade a las condiciones_numeros
                    if termino.isdigit():
                    
                        condiciones_numeros.append("p.nombre LIKE '%% {}kg%%'".format(termino))
                    

                    #Si no es un numero
                    else:
                        try:
                
                            #Intenta pasarlo a float para ver si es un decimal
                            termino=float(termino)
                                
                            #Si es un decimal se añade como si fuera un numero mas, con el kg
                            condiciones_numeros.append("p.nombre LIKE '%% {}kg%%'".format(termino))
        
                                
                        #Si falla es porque es una palabra   
                        except Exception as error:

                            if termino=='kg':
                                condiciones_kilos.append("p.nombre LIKE '%%{}%%'".format(termino))

                            #Si es alguna marca lo añade a las condiciones_marcas
                            elif termino in ['domyos','maniak','corength','e-series','kraftboost','tunturi']:
                                condiciones_marcas.append("p.nombre LIKE '%%{}%%'".format(termino))

                            #Si es un material lo añade a condiciones_materiales
                            elif termino in ['inclinado','plano','abierto','cuerda','metal','neutro','unilateral','estrecho','gironda','hierro','goma','metalico']:
                                condiciones_materiales.append("p.nombre LIKE '%%{}%%'".format(termino))

                            #Sino ya lo mete en condiciones_palabras    
                            else:
                                condiciones_palabras.append("p.nombre LIKE '%%{}%%'".format(termino))
                
                
                #Con cada lista, juntamos los strings con ors y dentro de parentesis, 
                # para que, cada grupo de condiciones si o si deban cumplirse
                if condiciones_palabras:
                    condiciones.append('({})'.format(' OR '.join(condiciones_palabras)))

                if condiciones_marcas:
                    condiciones.append('({})'.format(' OR '.join(condiciones_marcas)))

                if condiciones_materiales:
                    condiciones.append('({})'.format(' OR '.join(condiciones_materiales)))

                if condiciones_numeros:
                    condiciones.append('({})'.format(' OR '.join(condiciones_numeros)))
                
                if condiciones_kilos:
                    condiciones.append('({})'.format(' OR '.join(condiciones_kilos)))
            
            
            #Si hay condiciones, mete un WHERE y luego, los 
            # strings separados por ands usando el join
            if condiciones:
                
                #Si el admin es False, quiere decir que los productos los 
                # veran los clientes, y solo odeben ver los activos
                if not admin:
                    condiciones=' WHERE p.activo=1 AND '+' AND '.join(condiciones)
                else:
                    condiciones=' WHERE '+' AND '.join(condiciones)
                
                print('Las condiciones ya procesadas:',condiciones)
                
                return condiciones
                
            #Si no hay condicones devuelve nada 
            return ''
        
        #Si no hay parametros devuelve nada
        return ''


    #Funcion para /shop para devolver el total de productos que se 
    # necesitará para hacer lo de la paginacion
    @classmethod
    def mostrar_contador_productos(cls,db,parametros,categorias,admin=False):
        try:
            #Se abre un cursor con la conexion a la db
            cursor=db.connection.cursor()
        
            #Consulta base
            sql='SELECT COUNT(*) FROM productos p'
            
            #Dependiendo de si admin es True o False, pasamos al metodo construir where el admin
            if not admin:
                condiciones=cls.construir_where(parametros,categorias)
            else:
                condiciones=cls.construir_where(parametros,categorias,admin=True)

            #Añadimos als condicones al sql  
            sql+=condiciones

            #Si no hay condicones, y no es para el admin, 
            # añadimos que se muestren solo los productos 
            # activos
            if not condiciones:
                if not admin:
                    sql+=' WHERE p.activo=1'

            print('El sql final desde mostrar contador:',sql)
            
            #Ejecutamos la consulta
            cursor.execute(sql)
            resultados=cursor.fetchall()

            #Si hay resultados obtendrémos el count
            if resultados:
                cursor.close()
                return resultados[0][0]
                 
            
            #Si no hay resultados, retornamos None    
            else:
                cursor.close()
                return None
        
        
        #Si hay errores, devolvemos None tambien
        except Exception as error:
            print(error)
            return None
    
    
    #Funcion para /shop, donde se mostraran los productos y se filtraran con LIMIT y OFFSET
    # para que se muestren asi con la paginación
    @classmethod
    def mostrar_productos_paginacion(cls,db,page,productos_por_pagina,orden,parametros,categorias,admin=False):
        try:
            #Se abre un cursor con la conexion a la db
            cursor=db.connection.cursor()

            #El limit seran el numero de productos que apareceran
            # en este caso, los productos por pagina
            limit=productos_por_pagina

            #El offset es cuantos productos se saltará, pero claro, si page es 1, 
            # debe saltarse 0, por tanto restamos 1 a page
            offset=(page-1)*productos_por_pagina
            

            #Montamos la consulta base, que si es para el admin tendra 
            # nombre de marca y categoria, ventas, activo, etc...
            if not admin:
                sql='SELECT id,nombre,precio,imagen FROM productos p'
            else:
                sql='''
                    SELECT p.id,p.nombre,p.stock,p.precio,p.activo,p.ventas,p.fecha_registro,m.nombre,c.nombre FROM productos p 
                    INNER JOIN marcas m
                    ON p.id_marca=m.id
                    INNER JOIN categorias c
                    ON p.id_categoria=c.id
                '''


            #Dependiendo de si admin es True o False, pasamos al metodo construir where el admin
            if not admin:
                condiciones=cls.construir_where(parametros,categorias)
            else:
                condiciones=cls.construir_where(parametros,categorias,admin=True)

            #Añadimos las condicones al sql
            sql+=condiciones

            #Si no hay condicones, y no es para el admin, 
            # añadimos que se muestren solo los productos 
            # activos
            if not condiciones:
                if not admin:
                    sql+=' WHERE p.activo=1'


            #Mira el orden por cual filtrar
            if orden=='masRecientes':
                sql+=' ORDER BY p.id DESC'

            elif orden=='topVentas':
                sql+=' ORDER BY p.ventas DESC'


            #Añadimos al final el limit y el offset con /%s
            sql+=' LIMIT %s OFFSET %s'

            print('El sql final desde mostrar productos:',sql)

            values=(limit,offset)
            
            # #Ejecutamos la consulta
            cursor.execute(sql,values)
            resultados=cursor.fetchall()
           

            #Si la consulta devuelve datos, creamos una lista, recorremos los datos 
            # y creamos un objeto con cada producto, metiendolos en la lista
            if resultados:
                productos=[]

                if not admin:
                    for resultado in resultados:
                        
                        id=resultado[0]
                        nombre=resultado[1]
                        precio=resultado[2]
                        imagen=resultado[3]

                        productos.append(Product(id,nombre, precio, None, None, None, imagen))
                
                else:
                    #Si es para el admin, añadimos mas datos
                    for resultado in resultados:
                        id=resultado[0]
                        nombre=resultado[1]
                        stock=resultado[2]
                        precio=resultado[3]
                        activo=resultado[4]
                        ventas=resultado[5]
                        fecha_registro=resultado[6]
                        marca=resultado[7]
                        categoria=resultado[8]
                    
                        productos.append(Product(id,nombre,precio,marca,categoria,0,0,stock,ventas,activo,fecha_registro))

                cursor.close()
                return productos
                
            #Si no hay resultados, retornamos None    
            else:
                cursor.close()
                return None
        
        
        #Si hay errores, devolvemos None tambien
        except Exception as error:
            print(error)
            return None
        
    
    #Metodo para mostrar la informacion de u nproducto en su pagina 
    @classmethod
    def mostrar_producto_info(cls,db,id):

        try:
            #Abrimos como siempre el cursor
            cursor=db.connection.cursor()

            #Montamos una consulta con joins para obtener el nombre de la categoria y marca
            sql='''
                SELECT p.nombre as nombre_producto,p.precio,p.descripcion,p.imagen,p.stock,
                m.nombre as nombre_marca,
                c.nombre as nombre_categoria
                FROM productos p
                INNER JOIN marcas m ON p.id_marca=m.id
                INNER JOIN categorias c ON p.id_categoria=c.id
                WHERE p.id=%s and p.activo=1;
            '''

            #Ejecutamos
            cursor.execute(sql,(id,))
            resultado=cursor.fetchone()
           

            #SI hay resultado, metemos todos los campos devueltos en el objeto Product y retornamos eso
            if resultado:

                print('El resultado:',resultado)
                
                nombre_producto=resultado[0]
                precio=resultado[1]
                descripcion=resultado[2]
                imagen=resultado[3]
                stock=resultado[4]
                nombre_marca=resultado[5]
                nombre_categoria=resultado[6]


                producto=Product(id,nombre_producto,precio,nombre_marca,nombre_categoria,descripcion,imagen,stock)

            
                cursor.close()
                return producto
                
            #Si no hay resultados, retornamos None    
            else:
                cursor.close()
                return None
        
        
        #Si hay errores, devolvemos None tambien
        except Exception as error:
            print(error)
            return None
        

###################################################################################################
#Metodos para modo admin
        
    #Función para mostrar un producto
    @classmethod
    def getProduct(cls,db,id):
        try:
            #Se abre un cursor con la conexion a la db y se crea la consulta sql
            cursor=db.connection.cursor()

            #Mostramos todos los productos
            sql='''
                SELECT p.id,p.nombre,p.stock,p.precio,p.descripcion,p.imagen,m.nombre,c.nombre FROM productos p 
                INNER JOIN marcas m
                ON p.id_marca=m.id
                INNER JOIN categorias c
                ON p.id_categoria=c.id
                WHERE p.id=%s
                ORDER BY id DESC
            '''
            cursor.execute(sql,(id,))
            resultado=cursor.fetchone()
           
            #Si hay resultado, devolvemos el producto
            if resultado:

                id=resultado[0]
                nombre=resultado[1]
                stock=resultado[2]
                precio=resultado[3]
                descripcion=resultado[4]
                imagen=resultado[5]
                marca=resultado[6]
                categoria=resultado[7]

                cursor.close()
                    
                return Product(id,nombre,precio,marca,categoria,descripcion,imagen,stock)

                
            #Si no hay resultados, retornamos None    
            else:
                cursor.close()
                return None
        
        
        #Si hay errores, devolvemos None tambien
        except Exception as error:
            print(error)
            return None
        

    #Función para editar un producto
    @classmethod
    def setProduct(cls,db,product):
        try:
            #Se abre un cursor con la conexion a la db y se crea la consulta sql
            cursor=db.connection.cursor()

            #Actualizamos los campos requeridos en el producto
            sql='UPDATE productos SET nombre=%s,stock=%s,precio=%s,descripcion=%s,id_marca=%s,id_categoria=%s WHERE id=%s'
            cursor.execute(sql,(product.nombre,product.stock,product.precio,product.descripcion,product.nombre_marca,product.nombre_categoria,product.id))
            db.connection.commit()

            print('El row count:',cursor.rowcount)

            if cursor.rowcount==0:
                cursor.close()
                return 'Datos iguales'
            
            cursor.close()
            
            return True
           
        #Si hay errores, devolvemos None
        except Exception as error:
            print(error)
            return None
        
        
    #Funcion para activar/desactivar un producto
    @classmethod
    def setActiveProduct(cls,db,id):
        try:
            #Se abre el cursor de la db
            cursor=db.connection.cursor()

            #Actualizamos el activo en el producto
            sql='UPDATE productos SET activo=NOT activo WHERE id=%s'
            cursor.execute(sql,(id,))

            #Obtenemos el activo
            sql='SELECT activo FROM productos WHERE id=%s'
            cursor.execute(sql,(id,))

            resultados=cursor.fetchone()

            if resultados:
                activo=resultados[0]
                print('El activo',activo)

            #SI el producto está desactivado
            if activo==0:
            
                #Obtenemos la suma de la cantidad de los productos que estan en carrito
                sql='SELECT SUM(cantidad) FROM carrito WHERE id_producto=%s'
                cursor.execute(sql,(id,))

                resultado=cursor.fetchone()

                #Si hay resultados, definimos la cantidad
                if resultado and resultado[0] is not None:
                    cantidad=resultado[0]

                    #Si la cantidad es mayor a 0, sumamos esa cantidad al stock del producto
                    if cantidad>0:
                        sql='UPDATE productos SET stock=stock+%s WHERE id=%s'
                        cursor.execute(sql,(cantidad,id))

                #Borramos del carrito todos los registros de ese producto
                sql='DELETE FROM carrito WHERE id_producto=%s'
                cursor.execute(sql,(id,))

            
                #Borramos tambien los productos de favoritos
                sql='DELETE FROM favoritos WHERE id_producto=%s'
                cursor.execute(sql,(id,))

            db.connection.commit()

            cursor.close()

            return True
        
        
        #Cualquier error distitno, None también        
        except Exception as error:
            print('Error al activar/desactivar el producto')
            print(error)
            return None