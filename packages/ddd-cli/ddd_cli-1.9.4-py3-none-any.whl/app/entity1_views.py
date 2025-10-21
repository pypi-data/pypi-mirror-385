
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .utils.filter_dict import clean_dict_of_keys

# importa las excepciones personalizadas
from .domain.exceptions import (
    Entity1ValueError,
    Entity1ValidationError,
    Entity1AlreadyExistsError,
    Entity1NotFoundError,
    Entity1OperationNotAllowedError,
    Entity1PermissionError
)

# importa las excepciones de repositorio
from .infrastructure.exceptions import (
    ConnectionDataBaseError,
    RepositoryError
)

# Importar formularios específicos de la entidad
from app.entity1_forms import (
    Entity1CreateForm, 
    Entity1EditGetForm, 
    Entity1EditPostForm, 
    Entity1ViewForm
)

# Importar servicios específicos del dominio
from app.services.entity1_service import Entity1Service


def entity1_list(request):
    """
    Vista genérica para mostrar una lista de todas las instancias de entity1.
    """

    entity1List = [] #inicialize list

    # Obtener la lista del repositorio
    try:
        entity1List = Entity1Service().list()

    except (Entity1ValueError) as e:
        messages.error(request,  str(e))
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    # Renderizar la plantilla con la lista
    return render(request, 'app/entity1_web_list.html', {
        'entity1List': entity1List
    })


def entity1_create(request):
    """
    Vista genérica para crear una nueva instancia de entity1 utilizando un servicio.
    """

    if request.method == "POST":

        # Validar los datos del formulario
        form = Entity1CreateForm(request.POST, request.FILES)

        if form.is_valid():
            try:        
                form_data = form.cleaned_data

                # Obtener el ID de la entidad relacionada si existe
                external_id = request.POST.get('external_id', None)

                # Obtener la lista de ids de externals seleccionadas
                externals_ids = form_data.get('externals', [])

                # LLamar al servicio de creación
                Entity1Service().create(data=form_data, external_id=external_id, externals=externals_ids)

                # Mostrar mensaje de éxito y redirigir
                messages.success(request, f"Successfully created entity1")
                return redirect('app:entity1_list')

            except Entity1AlreadyExistsError as e:
                messages.error(request, "Already Exists Error: " + str(e))
            except (Entity1ValueError, Entity1ValidationError) as e:
                form.add_error(None, "Validation Error: " + str(e))
            except (ConnectionDataBaseError, RepositoryError) as e:
                messages.error(request, "There was an error accessing the database or repository: " + str(e))
            except Exception as e:
                messages.error(request, "An unexpected error occurred: " + str(e))
        else:
            messages.error(request, "There were errors in the form. Please correct them")
    else:
        # Formulario vacío para solicitudes GET
        form = Entity1CreateForm()

    # Renderizar la plantilla con el formulario
    return render(request, 'app/entity1_web_create.html', {'form': form}) 


def entity1_edit(request, id=None):
    """
    Vista genérica para editar una instancia existente de entity1 utilizando un servicio.
    """

    if id is None:
        # Redireccion si no se proporciona un ID
        return redirect('app:entity1_list')

    try:
        # Obtener los datos de la entidad desde el servicio
        entity1 = Entity1Service().retrieve(entity_id=id)

    except Entity1NotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))
        return redirect('app:entity1_list')
    except Entity1ValueError as e:
        messages.error(request,  "Value Error: " + str(e))
        return redirect('app:entity1_list')
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
        return redirect('app:entity1_list')
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))
        return redirect('app:entity1_list')

    if request.method == "POST":

        # Validar los datos del formulario
        form = Entity1EditPostForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                form_data = form.cleaned_data            
                
                # obtenemos del request los campos especiales del formulario
                # ejemplo: password = request.POST.get('password', None)
                # ejemplo: photo = request.FILES.get('photo', None)
                # y los enviamos como parametros al servicio de actualizacion

                # Obtener el ID de la entidad relacionada si existe
                external_id = request.POST.get('external_id', None)

                # Obtener la lista de ids de externals seleccionadas
                externals_ids = form_data.get('externals', [])         
                
                # Limpiar los campos no actualizables del diccionario de datos
                form_data = clean_dict_of_keys(form_data, keys=Entity1EditPostForm.ENTITY_NOT_UPDATABLE_FIELDS)

                # LLamar al servicio de actualización
                Entity1Service().update(entity_id=id, data=form_data, external_id=external_id, externals=externals_ids)

                # Mostrar mensaje de éxito
                messages.success(request, f"Successfully updated entity1")

                # Redireccionar a la lista de entity1s
                return redirect('app:entity1_list')

            except Entity1NotFoundError as e:
                messages.error(request,  "Not Found Error: " + str(e))                
            except (Entity1ValueError, Entity1ValidationError) as e:
                form.add_error(None, "Validation Error: " + str(e))
            except (ConnectionDataBaseError, RepositoryError) as e:
                messages.error(request, "There was an error accessing the database or repository: " + str(e))
            except Exception as e:
                messages.error(request, "An unexpected error occurred: " + str(e))

        else:
            messages.error(request, "There were errors in the form. Please correct them")

    # request.method == "GET":
    else:  
        # Initialize the form with existing data
        form = Entity1EditGetForm(initial={
            'id': entity1.get('id'),
            'attributeName': entity1.get('attributeName'),
            'attributeEmail': entity1.get('attributeEmail')
        })

    # Renderizar la plantilla con el formulario
    return render(request, 'app/entity1_web_edit.html', {'form': form})


def entity1_detail(request, id=None):
    """
    Vista genérica para mostrar los detalles de una instancia específica de entity1.
    """
    if id is None:
        return redirect('app:entity1_list')

    try:
        # Obtener los datos de la entidad desde el servicio
        entity1 = Entity1Service().retrieve(entity_id=id)

    except Entity1NotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))        
        return redirect('app:entity1_list')
    except Entity1ValueError as e:
        messages.error(request,  str(e))
        return redirect('app:entity1_list')
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
        return redirect('app:entity1_list')
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))
        return redirect('app:entity1_list')

    # Renderizar la plantilla con el formulario de vista
    form = Entity1ViewForm(initial={
        'attributeName': entity1.get('attributeName'),
        'attributeEmail': entity1.get('attributeEmail')
    })

    return render(request, 'app/entity1_web_detail.html', {'form': form})


def entity1_delete(request, id=None):
    """
    Vista genérica para eliminar una instancia existente de entity1 utilizando un servicio.
    """
    if id is None:
        messages.error(request, "Non Valid id to delete")
        return redirect('app:entity1_list')

    try:
        # LLamar al servicio de eliminación
        Entity1Service().delete(entity_id=id)
        messages.success(request, f"Successfully deleted entity1")

    except Entity1NotFoundError as e:
        messages.error(request,  "Not Found Error: " + str(e))             
    except (Entity1ValueError, Entity1ValidationError) as e:
        messages.error(request,  "Validation Error: " + str(e))
    except (ConnectionDataBaseError, RepositoryError) as e:
        messages.error(request, "There was an error accessing the database or repository: " + str(e))
    except Exception as e:
        messages.error(request, "An unexpected error occurred: " + str(e))

    return redirect('app:entity1_list')

