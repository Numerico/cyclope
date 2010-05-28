# *-- coding:utf-8 --*
"""
views
-----
Standard views for Cyclope models, to be used by FrontEndView derived objects
which should be declared in a frontend_views.py file for each app."""

# cyclope views are declared and registered
# in frontend.py files for each app

from django.template import loader, RequestContext
from django.http import Http404, HttpResponse
from django.core.xheaders import populate_xheaders
from django.core.exceptions import ObjectDoesNotExist

from cyclope.utils import template_for_request

def object_detail(request, content_object=None, slug=None, queryset=None, inline=False,
        template_name=None, extra_context=None,
        context_processors=None, template_object_name='object',
        mimetype=None):
    """
    Generic detail of an object.

    Arguments:
        ...

    Templates: ``<app_label>/<model_name>_detail.html``
    Context:
        object
            the object
    """
    if extra_context is None: extra_context = {}
    model = queryset.model

    obj = content_object

    if obj is None:
        if queryset and slug:
            try:
                obj = queryset.get(slug=slug)
            except ObjectDoesNotExist:
                raise Http404(
                    "No %s found matching the query" % (model._meta.verbose_name))
        else:
            raise AttributeError("Generic detail view must be called "
                                 "with a content_object or a slug.")
    if not template_name:
        template_name = "%s/%s_detail.html" % (
            model._meta.app_label, model._meta.object_name.lower())
    t = loader.get_template(template_name)

    c = RequestContext(request, {
        template_object_name: obj,
    }, context_processors)
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value

    if not inline:
        c['host_template'] = template_for_request(request)

        #TODO(nicoechaniz): this would be useful for debugging but needs work
        #import xml.dom.minidom as dom
        #pretty = dom.parseString(t.render(c).encode('utf8')).toprettyxml()
        #response = HttpResponse(pretty, mimetype=mimetype)

        response = HttpResponse(t.render(c), mimetype=mimetype)
        populate_xheaders(request, response, model,
                          getattr(obj, obj._meta.pk.name))
        return response

    else:
        c['host_template'] = 'cyclope/inline_view.html'
        return t.render(c)


def object_list(request, queryset, inline=False, paginate_by=None, page=None,
        allow_empty=True, template_name=None, template_loader=loader,
        extra_context=None, context_processors=None, template_object_name='object',
        mimetype=None):
    """
    Generic list of objects.

    Templates: ``<app_label>/<model_name>_list.html``
    Context:
        object_list
            list of objects
        is_paginated
            are the results paginated?
        results_per_page
            number of objects per page (if paginated)
        has_next
            is there a next page?
        has_previous
            is there a prev page?
        page
            the current page
        next
            the next page
        previous
            the previous page
        pages
            number of pages, total
        hits
            number of objects, total
        last_on_page
            the result number of the last of object in the
            object_list (1-indexed)
        first_on_page
            the result number of the first object in the
            object_list (1-indexed)
        page_range:
            A list of the page numbers (1-indexed).
    """
    if extra_context is None: extra_context = {}
    queryset = queryset._clone()
    if paginate_by:
        paginator = Paginator(queryset, paginate_by, allow_empty_first_page=allow_empty)
        if not page:
            page = request.GET.get('page', 1)
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                # Page is not 'last', nor can it be converted to an int.
                raise Http404
        try:
            page_obj = paginator.page(page_number)
        except InvalidPage:
            raise Http404
        c = RequestContext(request, {
            '%s_list' % template_object_name: page_obj.object_list,
            'paginator': paginator,
            'page_obj': page_obj,

            # Legacy template context stuff. New templates should use page_obj
            # to access this instead.
            'is_paginated': page_obj.has_other_pages(),
            'results_per_page': paginator.per_page,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'page': page_obj.number,
            'next': page_obj.next_page_number(),
            'previous': page_obj.previous_page_number(),
            'first_on_page': page_obj.start_index(),
            'last_on_page': page_obj.end_index(),
            'pages': paginator.num_pages,
            'hits': paginator.count,
            'page_range': paginator.page_range,
        }, context_processors)
    else:
        c = RequestContext(request, {
            '%s_list' % template_object_name: queryset,
            'paginator': None,
            'page_obj': None,
            'is_paginated': False,
        }, context_processors)
        if not allow_empty and len(queryset) == 0:
            raise Http404
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    if not template_name:
        model = queryset.model
        template_name = "%s/%s_list.html" % (model._meta.app_label, model._meta.object_name.lower())
    t = template_loader.get_template(template_name)

#    return HttpResponse(t.render(c), mimetype=mimetype)

    if not inline:
        c['host_template'] = template_for_request(request)
        response = HttpResponse(t.render(c), mimetype=mimetype)
        return response

    else:
        c['host_template'] = 'cyclope/inline_view.html'
        return t.render(c)