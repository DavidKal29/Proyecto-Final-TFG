//Menú Hamburguesa Lógica

//Obtenemos el boton para abrir o cerrar
boton_hamburguesa=document.getElementById('boton_hamburguesa')
boton_hamburguesa.addEventListener('click', ()=>{ 
    //Obtenemos el div que es el menu hamburguesa
    let menu=document.getElementById('menu_hamburguesa'); 
    
    //Vemos si el menu está escondido o no, y dependiendo de eso, lo escondemos o lo hacemos aparecer
    menu.style.right=menu.style.right==='0px'?'-100%':'0px';

    //Obtenemos el icono del boton
    let icono_boton=document.getElementById('icono_boton') 

    //Esto hace que si la classlist es una de esas, cambia a la otra
    icono_boton.classList.toggle("fa-bars"); 
    icono_boton.classList.toggle("fa-x");       
});



console.log('El pathname:',window.location.pathname);

//Si la ruta es cualquiera salvo /shop y /admin/products (por los filtros) y tiene parámetros
if (window.location.pathname!='/shop' && window.location.pathname!='/admin/products' && window.location.search){
    
    //Limpiamos los parámetros sin recargar la página
    let newUrl=window.location.origin+window.location.pathname
    window.history.replaceState({},document.title,newUrl)

    console.log('Cambiado con exito')

}
