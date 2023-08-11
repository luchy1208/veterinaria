$(function(){
    $("#fileFoto").on("change",mostrarImagen);
    $("#cbRolMenu").change(function(){
        
        if($("#cbRolMenu").val()=="Administrador"){
            location.href="/inicioAdministrador/";
        }
        if($("#cbRolMenu").val()=="Especialista"){
            location.href="/inicioEspecialista/";
        } 
        if($("#cbRolMenu").val()=="Tecnico"){
        location.href="/inicioTecnico/";
        }
        
    })
})
/**
 * A partir de la selección de una 
 * imagen en el control fileFoto del
 * formulario, se obtiene la url para
 * poder mostrarlo en un control tipo
 * IMG
 * @param {*} evento 
 */
function mostrarImagen(evento){
    const archivos = evento.target.files
    const archivo = archivos[0]
    const url = URL.createObjectURL(archivo)  
    $("#imagenMostrar").attr("src",url)
  }

  

function mostrarAlerta() {

    Swal.fire({
        title: '<strong>Quienes <u>Somos</u></strong>',
        icon: 'info',
        html:
          'You can use <b>bold text</b>, ' +
          'and other HTML tags',
        showCloseButton: true,
        showCancelButton: true,
        focusConfirm: false,
        confirmButtonText:
          '<i class="fa fa-thumbs-up"></i> Great!',
        confirmButtonAriaLabel: 'Thumbs up, great!',
        cancelButtonText:
          '<i class="fa fa-thumbs-down"></i>',
        cancelButtonAriaLabel: 'Thumbs down'
      })
  }