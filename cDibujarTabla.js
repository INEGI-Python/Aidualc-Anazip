
var arrControles={};
var arrControlesNoGuardables={};

function crearTabla(objConf)
{
	var tabla='<table width="'+objConf.anchoTabla+'">';
    var fila1='';
    var fila2='';
    var contColumnas=0;
    var elemento;
    var x;
    for(x=0;x<objConf.arrElementos.length;x++)
    {
    	elemento=objConf.arrElementos[x];
        if(elemento.control && ((elemento.control.tipo=='Hidden')||(elemento.control.tipo=='fechaSistema')))
        	continue;
        if(contColumnas==0)
        {
        	fila1='<tr id="fila_'+x+'">';
            fila2='<tr id="filaCtrl_'+x+'">';
            
        }
        

        if(elemento.validacion && elemento.validacion.indexOf('obl')>-1)
        {
            if(elemento.titulo.indexOf('*')==-1)
            {
                elemento.titulo=elemento.titulo+' *';
            }
        }
        
        var estilo='';
        if(elemento.paddingLeft)
	        estilo='style="padding-left: '+elemento.paddingLeft+'px"';
        
        fila1+='<td valign="top" colspan="'+elemento.numColumna+'" class="'+(elemento.thCls?elemento.thCls:'')+'"  '+(elemento.ancho?('width="'+elemento.ancho+'"'):'')+'  ><div '+estilo+' id="div_titulo_'+elemento.id+'" style="display:flex">'+((!elemento.ocultarTitulo)?elemento.titulo:'')+'</div></td>';
        fila2+='<td valign="top" colspan="'+elemento.numColumna+'" class="'+(elemento.tdCls?elemento.tdCls:'')+'"><div id="div_'+elemento.id+'" style="display:flex"></div></td>';
        
        
        contColumnas+=parseInt(elemento.numColumna);
        if(contColumnas>=objConf.totalColumna)
        {
        	contColumnas=0;
            fila1+='</tr>';
            fila2+='</tr>';
        	tabla+=fila1+fila2;
        }
        
        
        
        
    }
    
    if(contColumnas>0)
    {    
        for(x=contColumnas;x<objConf.totalColumna;x++)
        {
            fila1+='<td></td>';
            fila2+='<td></td>';
    
            if(x>=objConf.totalColumna-1)
            {
                contColumnas=0;
                fila1+='</tr>';
                fila2+='</tr>';
                tabla+=fila1+fila2;
                break;
            }
        }
    }
    tabla+='</table>';
    
    gE(objConf.renderTo).innerHTML=tabla;
    
    contruirControles(objConf);
}

function contruirControles(objConf)
{
	var elemento;
    var x;
    arrControles[objConf.id]=[];
            
    for(x=0;x<objConf.arrElementos.length;x++)
    {
    	elemento=objConf.arrElementos[x];
        if(elemento.control)
        {
        	var prefijo='Ext.form.';
            if(elemento.control.tipo=='Button')
            	prefijo='Ext.';
        	var objConfControl={};
            objConfControl.id='idCtrl_'+elemento.id;
            
            var esFechaSistema=false;
            if(elemento.control.tipo=='fechaSistema')
            {
            	esFechaSistema=true;
                elemento.control.tipo='Hidden';
            }
            
			if(elemento.control.tipo!='Hidden')
	            objConfControl.renderTo='div_'+elemento.id;
            if(elemento.control.propiedades)
            {
            
            	for(campo in elemento.control.propiedades)
    			{
	                objConfControl[campo]=elemento.control.propiedades[campo];
                	
                }
            }
           	
            
            if(elemento.control.eventos)
            {
            	objConfControl.listeners={};
            	for(campo in elemento.control.eventos)
    			{
                	objConfControl.listeners[campo]=elemento.control.eventos[campo];
                }
            }
             
             
            if(elemento.caracteresPermitidos || elemento.longitudMaxima || elemento.convertirMayusculas || elemento.funcionValidacionCaracter)
            {
            	objConfControl['enableKeyEvents']=true;
            } 
            
            
            var ctrl;
            
            if(elemento.control.tipo!='combobox')
            { 
                var controlTxt='ctrl=new '+prefijo+elemento.control.tipo+'(objConfControl);'
                
                eval(controlTxt);
                
                
			}
            else
            {
            	ctrl=crearComboExt('idCtrl_'+elemento.id,elemento.control.arrDatos,0,0,elemento.control.propiedades.width,objConfControl);
                
                
                for(campo in elemento.control.eventos)
    			{
                	ctrl.on(campo,elemento.control.eventos[campo]);
                    

                }
                if(elemento.control.propiedades.disabled)
                {
                	ctrl.disable();
                }
                gE('div_'+elemento.id).style.width=(elemento.control.propiedades.width+10)+'px';
                
            }
            ctrl.validacion=elemento.validacion?elemento.validacion:'';
            ctrl.titulo=elemento.titulo?elemento.titulo.replace(':',''):'';
            
            if(ctrl.validacion.indexOf('obl')>-1)
            {
            	if(ctrl.titulo.indexOf('*')==-1)
                {
                	ctrl.titulo=ctrl.titulo+' *';
                }
            }
            
            
            ctrl.caracteresPermitidos=elemento.caracteresPermitidos?elemento.caracteresPermitidos:'';
            ctrl.longitudMaxima=elemento.longitudMaxima?elemento.longitudMaxima:'';
            ctrl.convertirMayusculas=elemento.convertirMayusculas?elemento.convertirMayusculas:false;
            ctrl.esFechaSistema=esFechaSistema;
            ctrl.on('change',function(ctrl)
            					{
                                	var divControl=gE(ctrl.getId().replace('idCtrl_','div_'));
                                    var clase=divControl.getAttribute('class');
                                	if(clase)
                                    {
                                    	divControl.setAttribute('class',clase.replace('ctrlSeleccionado',''));
                                    }
                                	
                                }
                                
            		)
                    
            if(objConf.soloLectura)
            {
            	ctrl.disable();
            }        
                    
            if(elemento.caracteresPermitidos || elemento.longitudMaxima || elemento.funcionValidacionCaracter)
            {
            	if(elemento.funcionValidacionCaracter)
                	ctrl.funcionValidacionCaracter=elemento.funcionValidacionCaracter;
            	ctrl.on('keypress',function(ctrl,e)
                					{
                                    
                                    	
                                    
                                    	if(ctrl.caracteresPermitidos!='')
                                        {
                                        	var caracter=String.fromCharCode(e.charCode);
                                            if(!ctrl.caracteresPermitidos.test(caracter))
                                            {
                                                e.stopEvent();
                                            }
                                        }
                                        
                                        if(ctrl.longitudMaxima!='')
                                        {
                                        	if(ctrl.getValue().length>=ctrl.longitudMaxima)
                                            {
                                            	e.stopEvent();
                                            }
                                            
                                            
                                        }
                                        
                                        if(ctrl.funcionValidacionCaracter)
                                        {

                                        	if(!ctrl.funcionValidacionCaracter(ctrl,caracter))
                                            {
                                            	e.stopEvent();
                                            }
                                        }
                                        
                                        
                                    
                                    
                                    }
                        )
            }
            
            if(elemento.convertirMayusculas)
            {
            	ctrl.on('keyup',function(ctrl,e)
                					{
                                    	if(ctrl.convertirMayusculas)
                                        {

                                            ctrl.setValue(ctrl.getValue().toUpperCase());	
                                        }
                                    
                                    
                                    }
                        )
            }
            
            
            if(elemento.control && elemento.control.propiedades && elemento.control.propiedades.valor && elemento.control.propiedades.valor!='')
            {
            	//ctrl.fireEvent( 'change', elemento.control.propiedades.valor,'' );
                if(elemento.control.tipo=='combobox')
                {
                	dispararEventoSelectCombo(ctrl.getId());
//                	ctrl.fireEvent( 'select', ctrl,registro,indice );
                    
                    
                }
                

                 
            }
                    
            arrControles[objConf.id].push(ctrl)
            
            if((typeof(elemento.guardable)!='undefined')&&(!elemento.guardable))
            {
            	if(!arrControlesNoGuardables[objConf.id])
                	arrControlesNoGuardables[objConf.id]={};
            	arrControlesNoGuardables[objConf.id][ctrl.getId()]=1;
            }
            
        }
    }
    

}

function addControl(objConf)
{
	
    for(x=0;x<objConf.arrElementos.length;x++)
    {
    	elemento=objConf.arrElementos[x];
    	var nodo=cE('span');
        nodo.id='span_'+elemento.id;
        
        if(elemento.paddingLeft)
	        nodo.style='padding-left: '+elemento.paddingLeft+'px';
        
        
    	gE(elemento.control.innerObject).appendChild(nodo);
    
        
        if(elemento.control)
        {
            var prefijo='Ext.form.';
            if(elemento.control.tipo=='Button')
                prefijo='Ext.';
            var objConfControl={};
            objConfControl.id='idCtrl_'+elemento.id;
            
            var esFechaSistema=false;
            if(elemento.control.tipo=='fechaSistema')
            {
                esFechaSistema=true;
                elemento.control.tipo='Hidden';
            }
            
            if(elemento.control.tipo!='Hidden')
                objConfControl.renderTo='span_'+elemento.id;
            if(elemento.control.propiedades)
            {
            
                for(campo in elemento.control.propiedades)
                {
                    objConfControl[campo]=elemento.control.propiedades[campo];
                    
                }
            }
            
            
            if(elemento.control.eventos)
            {
                objConfControl.listeners={};
                for(campo in elemento.control.eventos)
                {
                    objConfControl.listeners[campo]=elemento.control.eventos[campo];
                }
            }
             
             
            if(elemento.caracteresPermitidos || elemento.longitudMaxima || elemento.convertirMayusculas)
            {
                objConfControl['enableKeyEvents']=true;
            } 
            
            
            var ctrl;
            
            if(elemento.control.tipo!='combobox')
            { 
                var controlTxt='ctrl=new '+prefijo+elemento.control.tipo+'(objConfControl);'
                
                eval(controlTxt);
                
                
            }
            else
            {
                ctrl=crearComboExt('idCtrl_'+elemento.id,elemento.control.arrDatos,0,0,elemento.control.propiedades.width,objConfControl);
                
                
                for(campo in elemento.control.eventos)
                {
                    ctrl.on(campo,elemento.control.eventos[campo]);
                    
    
                }
                
                gE('div_'+elemento.id).style.width=(elemento.control.propiedades.width+10)+'px';
                
            }
            ctrl.validacion=elemento.validacion?elemento.validacion:'';
            ctrl.titulo=elemento.titulo?elemento.titulo.replace(':',''):'';
            
            if(ctrl.validacion.indexOf('obl')>-1)
            {
            	if(ctrl.titulo.indexOf('*')==-1)
                {
                	ctrl.titulo=ctrl.titulo+' *';
                }
            }
            
            ctrl.caracteresPermitidos=elemento.caracteresPermitidos?elemento.caracteresPermitidos:'';
            ctrl.longitudMaxima=elemento.longitudMaxima?elemento.longitudMaxima:'';
            ctrl.convertirMayusculas=elemento.convertirMayusculas?elemento.convertirMayusculas:false;
            ctrl.esFechaSistema=esFechaSistema;
            ctrl.on('change',function(ctrl)
                                {
                                    var divControl=gE(ctrl.getId().replace('idCtrl_','div_'));
                                    var clase=divControl.getAttribute('class');
                                    if(clase)
                                    {
                                        divControl.setAttribute('class',clase.replace('ctrlSeleccionado',''));
                                    }
                                    
                                }
                                
                    )
        	if(objConf.soloLectura)
            {
            	ctrl.disable();
            }            
                    
                    
            if(elemento.caracteresPermitidos || elemento.longitudMaxima)
            {
                ctrl.on('keypress',function(ctrl,e)
                                    {
                                        if(ctrl.caracteresPermitidos!='')
                                        {
                                            var caracter=String.fromCharCode(e.charCode);
                                            if(!ctrl.caracteresPermitidos.test(caracter))
                                            {
                                                e.stopEvent();
                                            }
                                        }
                                        
                                        if(ctrl.longitudMaxima!='')
                                        {
                                            if(ctrl.getValue().length>=ctrl.longitudMaxima)
                                            {
                                                e.stopEvent();
                                            }
                                            
                                            
                                        }
                                        
                                        
                                    
                                    
                                    }
                        )
            }
            
            if(elemento.convertirMayusculas)
            {
                ctrl.on('keyup',function(ctrl,e)
                                    {
                                        if(ctrl.convertirMayusculas)
                                        {
    
                                            ctrl.setValue(ctrl.getValue().toUpperCase());	
                                        }
                                    
                                    
                                    }
                        )
            }
            
            
            if(elemento.control && elemento.control.propiedades && elemento.control.propiedades.valor && elemento.control.propiedades.valor!='')
            {
                //ctrl.fireEvent( 'change', elemento.control.propiedades.valor,'' );
                if(elemento.control.tipo=='combobox')
                {
                    dispararEventoSelectCombo(ctrl.getId());
                    
                    
                }
                
    
                 
            }
                    
            arrControles[objConf.id].push(ctrl)
            
            if((typeof(elemento.guardable)!='undefined')&&(!elemento.guardable))
            {
                if(!arrControlesNoGuardables[objConf.id])
                    arrControlesNoGuardables[objConf.id]={};
                arrControlesNoGuardables[objConf.id][ctrl.getId()]=1;
            }
            
        }
    }
    	
}

function limpiarControles(idEstructura)
{
	var x;
    var control;
    var cadObj='';
    
    if(!arrControles[idEstructura])
    	return;
    
    var aControles=arrControles[idEstructura];
    
    for(x=0;x<aControles.length;x++)
    {
    	control=aControles[x];
        
    	if(control.setValue)
        {
        	
            control.setValue('');
        
        }
        else
        {
        	if(control.value)
            {
                
                control.value='';
            
            }
        }
    }
    
   
    	
}


function obtenerValores(idEstructura)
{
	var x;
    var control;
    var cadObj='';
    var aControles=arrControles[idEstructura];
    
    for(x=0;x<aControles.length;x++)
    {
    	control=aControles[x];
        
    	if((control.getValue)&& (!arrControlesNoGuardables[idEstructura] ||(!arrControlesNoGuardables[idEstructura][control.getId()])))
        {
        	
            if(control.getValue().format)
            {
            	console.log(control);
            }
            
            var valor=control.getValue();
            if(valor.format)
            	valor=valor.format('Y-m-d');
            
            
        	var token='"'+control.getId().replace('idCtrl_','')+'":"'+cv(valor)+'"';
        	if(cadObj=='')
            	cadObj=token;
            else
            	cadObj+=','+token;
        
        }
    }
    
    cadObj='{'+cadObj+'}';
    return cadObj;
    	
}


function validarControles(idEstructura,resaltarError)
{
	var arrValidaciones;
	var aControles=arrControles[idEstructura];
    var x;
    var control;
    for(x=0;x<aControles.length;x++)
    {
    	control=aControles[x];
        
        if(!arrControlesNoGuardables[idEstructura] || !arrControlesNoGuardables[idEstructura][control.getId()])
        {
        
            if(control.validacion!='')
            {
                arrValidaciones=aControles[x].validacion.split('|');
                
                var pos;
                for(pos=0;pos<arrValidaciones.length;pos++)
                {
                    switch(arrValidaciones[pos])
                    {
                        case 'obl':
                            if((control.getValue()+'').trim()=='')
                            {
                                function respObl()
                                {
                                    control.focus();
                                    if(resaltarError)
                                    {
                                    
                                        setDivError(control);
                                    }
                                }
                                msgBox('El campo "'+control.titulo+'" es obligatorio',respObl);
                            
                                return false;
                            }
                            
                            
                            
                        break;
                        case 'num':
                            var valor=(control.getValue()+'').trim();
                            if(valor=='')
                                valor='0';
                            valorEnt=parseInt(normalizarValor(valor));
                            if((isNaN(valorEnt))||(valor.indexOf('.')>=0))
                            {
                                
                                function respNum()
                                {
                                    control.focus();
                                    if(resaltarError)
                                    {
                                    
                                        setDivError(control);
                                    }
                                }
                                msgBox('El valor del campo "'+control.titulo+'" no es v&aacute;lido',respNum);
                            
                                return false;
                            }
                            
                        break;
                        case 'flo':
                            var valor=(control.getValue()+'').trim();
                            if(valor=='')
                                valor='0';
                            valorEnt=parseFloat(normalizarValor(valor));
                            var arrComas=valor.split('.');
                            
                            
                            if(isNaN(valorEnt) ||(arrComas.length>2))
                            {
                                function respFlo()
                                {
                                    control.focus();
                                    if(resaltarError)
                                    {
                                    
                                        setDivError(control);
                                    }
                                }
                                msgBox('El valor del campo "'+control.titulo+'" no es v&aacute;lido',respFlo);
                            
                                return false;
                            }
                           
                        break;
                        case 'dte':
                            var Cadena='';
                            var tipo=typeof(control.getValue());
                            if(tipo=='string')
                            {
                                if(control.getValue().indexOf('-')>-1)
                                {
                                    var arrFecha=control.getValue().split('-');
                                    Cadena=arrFecha[2]+'/'+arrFecha[1]+'/'+arrFecha[0];
                                }
                                else
                                    Cadena=control.getValue().trim();
                            }
                            else
                            {
                                Cadena=control.getValue().format('d/m/Y');
                            }
                        
                            var Fecha= new String(Cadena);   
                            var RealFecha= new Date();   
                            var Ano= new String(Fecha.substring(Fecha.lastIndexOf("/")+1,Fecha.length));  
                            var Mes= new String(Fecha.substring(Fecha.indexOf("/")+1,Fecha.lastIndexOf("/")));
                            var Dia= new String(Fecha.substring(0,Fecha.indexOf("/")));
                           
                            if (Ano=='' || isNaN(Ano) || Ano.length<4 || parseFloat(Ano)<1900)
                            {
                                function respDte1()
                                {
                                    control.focus();
                                    if(resaltarError)
                                    {
                                        setDivError(control);
                                    }
                                }
                                msgBox('La fecha ingresada en campo "'+control.titulo+'" no es v&aacute;lida',respDte1);
                                return false ; 
                            }
                            if (Mes=='' || isNaN(Mes) || parseFloat(Mes)<1 || parseFloat(Mes)>12)
                            {
                                function respDte2()
                                {
                                    control.focus();
                                    if(resaltarError)
                                    {
                                        setDivError(control);
                                    }
                                }
                                msgBox('La fecha ingresada en campo "'+control.titulo+'" no es v&aacute;lida',respDte2);
                                return false ;  
                            }
                             
                            if (Dia=='' || isNaN(Dia) || parseInt(Dia, 10)<1 || parseInt(Dia, 10)>31)
                            {
                                function respDte3()
                                {
                                    control.focus();
                                    if(resaltarError)
                                    {
                                        setDivError(control);
                                    }
                                }
                                msgBox('La fecha ingresada en campo "'+control.titulo+'" no es v&aacute;lida',respDte3);
                                return false ; 
                            }
                            if (Mes==4 || Mes==6 || Mes==9 || Mes==11 || Mes==2) 
                            {  
                                if (Mes==2 && Dia > 28 || Dia>30) 
                                {
                                    function respDte4()
                                    {
                                        control.focus();
                                        if(resaltarError)
                                        {
                                            setDivError(control);
                                        }
                                    }
                                    msgBox('La fecha ingresada en campo "'+control.titulo+'" no es v&aacute;lida',respDte4);
                                    return false ;  
                                }
                            }  

                        break;
                        case 'mail':
                        
                            var valor=(control.getValue()+'').trim();
                            var filter=/^[A-Za-z0-9\._\-]+@[A-Za-z0-9_\-]+(\.[A-Za-z]+){1,2}$/;
                            if (valor.length == 0 ) 
                                return true;
                            if (!filter.test(valor))
                            {
                                function respMail()
                                {
                                    control.focus();
                                    if(resaltarError)
                                    {
                                        setDivError(control);
                                    }
                                }
                                msgBox('La direcci&oacute; ingresada en campo "'+control.titulo+'" no es v&aacute;lida',respMail);
                                return false ; 
                            }
                        
                            
                        break;
                    }
                }
                
                
                
            }
    	}
    }
    
    return true;
    
}

function setDivError(control)
{
	var divControl=gE(control.getId().replace('idCtrl_','div_'));
                                
	divControl.setAttribute('class',(divControl.getAttribute('class')?(divControl.getAttribute('class')+' '):'')+'ctrlSeleccionado');
}

function guardarValores(objConf)
{
	var x;
    var control;
    var cadObj='';
    var aControles=arrControles[objConf.idEstructura];
    
    var aValorEnvia;
    
    var formData = new FormData();
  	formData.append('tabla',objConf.tabla); 
    formData.append('id',objConf.id); 
    formData.append('campoId',objConf.campoId); 
    
    for(x=0;x<aControles.length;x++)
    {
    
    	control=aControles[x];
    	if(!arrControlesNoGuardables[objConf.idEstructura][control.getId()])
        {
            
            aValorEnvia=normalizarValorControl(control);
            formData.append(aValorEnvia[0],aValorEnvia[1]);
		}    

    	
    }
    
    $.ajax(objConf.url, {
                            method: objConf.metodo,
                            data: formData,
                            processData: false,
                            contentType: false,
                            success: function (response) 
                                        {
                                            var arrResp=response.split('|');
                                            
                                            ocultarMensajeProcesando();
                                        
                                        },
                            error: function () 
                                    {
                                    }
                          }
                       );
    
}


function normalizarValorControl(ctrl)
{

	var aValor=[];


	var idNormalizado=ctrl.getId().replace('idCtrl_','');
    idNormalizado='_'+idNormalizado;
    var valorControl='';
    
    
    switch(ctrl.getXType() )
    {
    	case 'hidden':
        	if(ctrl.esFechaSistema)
            	idNormalizado+='dts';
            else
        		idNormalizado+='vch';
            valorControl=ctrl.getValue();
        break;
        case 'numberfield':
        	idNormalizado+='flo';
            valorControl=ctrl.getValue();
        break;
        case 'datefield':
        	idNormalizado+='dte';
            valorControl=ctrl.getValue().format('Y-m-d');
        break;
    	default:
        	
        	idNormalizado+='vch';
            valorControl=ctrl.getValue();
         break;
    }
	aValor[0]=idNormalizado;
    aValor[1]=valorControl;
    
    
    
	return aValor;
}

function setValores(idEstructura,objValores)
{
	var idControl;
	var control;
    var aControles=arrControles[idEstructura];
    for(x=0;x<aControles.length;x++)
    {
    	control=aControles[x];
        idControl=control.getId().replace('idCtrl_','');
        if(objValores[idControl])
        {
        	control.setValue(objValores[idControl]);
        }
        
    }
    
    
}

function cargarValores(objConf)
{
	var formData = new FormData();
  	formData.append('tabla',objConf.tabla); 
    formData.append('id',objConf.id); 
    formData.append('campoId',objConf.campoId); 
    
    if(objConf.params)
    {
    	var x;
        for(x=0;x<objConf.params.length;x++)
        {
            formData.append(objConf.params[x][0],objConf.params[x][1]);
        }
	}    
    $.ajax(objConf.url, {
                            method: objConf.metodo,
                            data: formData,
                            processData: false,
                            contentType: false,
                            success: function (response) 
                                        {
                                            var arrResp=response.split('|');
                                            var objCarga=eval(arrResp[1])[0];
                                            
                                            setValores(objConf.idEstructura,objCarga)
                                            
                                            ocultarMensajeProcesando();
                                        
                                        },
                            error: function () 
                                    {
                                    }
                          }
                       );
    
}
