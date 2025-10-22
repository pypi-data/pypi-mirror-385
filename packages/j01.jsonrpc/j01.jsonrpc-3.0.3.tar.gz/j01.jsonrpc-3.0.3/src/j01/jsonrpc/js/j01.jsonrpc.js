/**
 * @fileoverview JSON-RPC handler methods used in j01.jsonrpc form and buttons
 *
 * @author Roger Ineichen dev at projekt01 dot ch
 * @version 1.0.1
 *
 */
//-----------------------------------------------------------------------------

var j01HTMLBody = $('html, body');

// -----------------------------------------------------------------------------
// callback registry
// -----------------------------------------------------------------------------
var j01CallbackRegistry = []; // new Array();

function j01RegisterCallback(cbName, callback, override) {
    // register callback by name and raise error if exists.
    // the callback method is used as response callback.
    if (typeof(override) === 'undefined') {
        // allows to override existing methods, otherwise raise alert
        override = false;
    }
    var key;
    for (key in j01CallbackRegistry) {
        if (key === cbName && override !== true) {
            // callback already registered
            var msg = "callback method " +cbName+ "already exists. ";
            msg += "Use j01OverrideCallback instead of j01RegisterCallback ";
            msg += "or use override=true";
            // this will raise an alert because your page will not work
            alert(msg); // p01.checker.silence
        }
    }
    // add callback if not exists
    j01CallbackRegistry[cbName] = callback;
}

function j01OverrideCallback(cbName, callback) {
    // register callback and don't riase error if exists
    j01CallbackRegistry[cbName] = callback;
}

function j01GetCallback(cbName, fallback) {
    if (typeof(fallback) === 'undefined') {
        // fallback to default (generic) callback if not defined. This allows
        // to use null as default for get a callback for onTimeout
        fallback = j01RenderContent;
    }
    // get callback by name
    if (typeof(cbName) === 'string') {
        var key;
        for (key in j01CallbackRegistry) {
            if (key === cbName) {
                // return this callback method
                return j01CallbackRegistry[cbName];
            }
        }
    }
    // given fallback method or if not defined j01RenderContent get used
    return fallback;
}

// -----------------------------------------------------------------------------
// render method helpers
// -----------------------------------------------------------------------------

function j01RenderHTMLAndBodyMarkers(response) {
    if (typeof(response.cssHTMLClass) === 'string') {
        $('html').removeClass().addClass(response.cssBodyClass);
    }
    if (typeof(response.cssBodyClass) === 'string') {
        $('body').removeClass().addClass(response.cssBodyClass);
    }
    if (typeof(response.cssHTMLId) === 'string') {
        $('html').attr('id', response.cssHTMLId);
    }
    if (typeof(response.cssBodyId) === 'string') {
        $('body').attr('id', response.cssBodyId);
    }
}

// scroll to handler (if scrollToExpression is given)
function j01RenderScrollToProcessing(response) {
    // process scrollTo
    if (typeof(response.scrollToExpression) === 'string') {
        var container = $(response.scrollToExpression);
        if (container) {
            // get previous height
            var wHeight = $(window).height();
            var sOffset = container.offset();
            if (container && sOffset) {
                var scrollTop = sOffset.top;
                if (response.scrollToOffset) {
                    scrollTop += response.scrollToOffset;
                }
                if (scrollTop >= wHeight) {
                    if (response.scrollToSpeed) {
                        scrollToSpeed = response.scrollToSpeed
                    } else {
                        scrollToSpeed = 500;
                    }
                    // scroll, but only if outside viewport and only the missing
                    // height
                    scrollTop -= wHeight;
                    j01HTMLBody.animate({'scrollTop': scrollTop}, scrollToSpeed);
                }
            }
        }
    }
}

// -----------------------------------------------------------------------------
// render method registry
// -----------------------------------------------------------------------------

var j01RenderMethodRegistry = []; // new Array();

function j01RegisterRenderMethod(mName, method, override) {
    // register method by name and raise error if exists.
    // the method method is used as response method.
    if (typeof(override) === 'undefined') {
        // allows to override existing methods, otherwise raise alert
        override = false;
    }
    // skip our default handler j01RenderContent
    var key;
    for (key in j01RenderMethodRegistry) {
        if (key === mName && override !== true) {
            // method already registered
            var msg = "method method " +mName+ "already exists. ";
            msg += "Use override=true";
            // this will raise an alert because your page will not work
            alert(msg); // p01.checker.silence
        }
    }
    // add method if not exists
    j01RenderMethodRegistry[mName] = method;
}

function j01GetRenderMethod(mName) {
    if (typeof(mName) === 'string') {
        // get render method by mName
        if (mName) {
            var key;
            for (key in j01RenderMethodRegistry) {
                if (key === mName) {
                    // return this callback method
                    return j01RenderMethodRegistry[mName];
                }
            }
        }
    }
    // return default render method if not found
    return j01RenderContentTargetExpression;
}

function j01RenderContentTargetExpression(response, contentTargetExpression) {
    // default method for render content into dom based on
    // given contentTargetExpression
    if (typeof(response.contentTargetExpression) === 'string') {
        // page contentTargetExpression as first
        var contentContainer = $(response.contentTargetExpression);
    }else if (typeof(contentTargetExpression) === 'string') {
        // given contentTargetExpression as next if page doesn't define
        // a contentTargetExpression
        var contentContainer = $(contentTargetExpression);
    }else{
        // default as fallback as last, if page use None which is the
        // default value (JSONRPCFormMixin.contentTargetExpression = None)
        var contentContainer = $('#content');
    }
    // apply html and body classes before insert content otherwise we will
    // not have the correct width
    j01RenderHTMLAndBodyMarkers(response);
    // inject content
    contentContainer.empty();
    contentContainer.html(response.content);
    // process optional scrollTo
    j01RenderScrollToProcessing(response, contentContainer);
}

// -----------------------------------------------------------------------------
// load content processor
// -----------------------------------------------------------------------------

// process load content used by click event handler function
function j01LoadContentProcessor(url, callback, onError, onTimeout, isPushState, requestId) {
    // trigger loading event on body tag
    $(document).trigger('j01.jsonrpc.loading')
    proxy = getJSONRPCProxy(url);
    proxy.addMethod('j01LoadContent', callback, onError, onTimeout, isPushState, requestId);
    var params = j01URLToArray(url);
    if (params) {
        proxy.j01LoadContent(params);
    } else {
        proxy.j01LoadContent();
    }
}

// -----------------------------------------------------------------------------
// callback (response) handler
// -----------------------------------------------------------------------------
// generic error handling
function j01RenderContentError(response, errorTargetExpression) {
    /* handle error response
     * see: z3c.publisher.interfaces.IJSONRPCErrorView
     * The z3c.publisher returns the following error data for jsonrpc 2.0:
     *
     * {'jsonrpc': self._request.jsonVersion,
     *  'error': {'code': result.code,
     *  'message': '<server error message>',
     *  'data': {
     *      'i18nMessage': '<optional i18n server error message>'
     *      'nextURL': '<optional url for unauthorized page access>'
     *      'errorTargetExpression': '<optional target css selector>'
     *  },
     *  'id': self._request.jsonId
     * }
     *
     * Note, the error returned is based on a error view and not based on the
     * page you where trying to access. This means such an error handling
     * concept must be a global concept and can't depend on a page setup.
     *
     * Hint: register your own error handler as your render callback method and
     * do whatever you need to do for present the error in your layout.
     * Ths implementation simply renders the returned content into the
     * element with the id j01Error or trigger an j01.jsonrpc.error JQuery
     * event. You can probably use this event for insert a nice message into
     * the dom
     */
    if (typeof(errorTargetExpression) === 'undefined') {
        var errorTargetExpression = '#j01Error';
    }
    var msg;
    if (typeof(response.data.nextURL) !== 'undefined') {
        // support unauthorized jsonrpc error view
        window.location.href = response.data.nextURL;
    } else {
        if (response.data.i18nMessage){
            msg = response.data.i18nMessage;
        }else {
            msg = response.message;
        }
        // find location defined in JSONRPCErrorView or use default
        var contentContainer;
        if (response.data.errorTargetExpression) {
            contentContainer = $(response.data.errorTargetExpression);
        } else {
            contentContainer = $(errorTargetExpression);
        }
        if (contentContainer && contentContainer.get(0)) {
            // render new content
            contentContainer.empty();
            contentContainer.html(msg);
        } else {
            // if errorTargetExpression not available
            $(document).trigger({
                type: 'j01.jsonrpc.error',
                msg: msg,
            });
        }
        // trigger loaded event on document
        $(document).trigger('j01.jsonrpc.loaded');
    }
}

// generic success handling
function j01RenderContentSuccess(response, contentTargetExpression) {
    // start processing
    if (response.nextURL) {
        // handle redirect based on given nextURL agument
        window.location.href = response.nextURL;
    }else if (response.nextContentURL) {
        // load content from nextContentURL
        var onSuccess = j01RenderContentSuccess,
            onError = j01RenderContentError,
            onTimeout = null,
            isPushState = false,
            id = 'nextContentURL';
        proxy = getJSONRPCProxy(response.nextContentURL);
        proxy.addMethod('j01LoadContent', onSuccess, onError, onTimeout,
            isPushState, id);
        try {
            params = j01URLToArray(response.nextContentURL);
        } catch(e) {
            params  = false;
        }
        if (params) {
            proxy.j01LoadContent(params);
        }else{
            proxy.j01LoadContent();
        }
    } else {
        // render new content into dom based on contentRenderMethodName
        var j01RenderMethod = j01GetRenderMethod(response.contentRenderMethodName);
        // render content based on contentRenderMethodName
        j01RenderMethod(response, contentTargetExpression);
        // process browser history state, j01.proxy will apply isPushState
        // based on jsonrpc method setup to the repsonse if not already given
        // in response
        if (typeof response.isPushState !== 'undefined' && response.isPushState) {
            // Note: the isPushState marker allows to block apply a history
            // state based on javascript setup independent from the page
            // response.
            // IMPORTANT: this marker is very important because we need to
            // prevent apply a history state if we load the page based on a
            // history state
            j01PushState(response);
        }
        // trigger loaded event on document
        $(document).trigger('j01.jsonrpc.loaded');
    }
}

// generic success and error response handler (only works with jsonrpc 2.0)
function j01RenderContent(response) {
    if (response.code) {
        // error handling
        j01RenderContentError(response, '#j01Error');
    } else {
        // success handling
        j01RenderContentSuccess(response, '#content');
    }
}

// register default response handler
j01RegisterCallback('j01RenderContentSuccess', j01RenderContentSuccess);
j01RegisterCallback('j01RenderContentError', j01RenderContentError);


// -----------------------------------------------------------------------------
// content loader
// -----------------------------------------------------------------------------
// content loader offering defaults
var J01ContentLoader = function (options) {
    this.options = $.extend({
        onSuccess: 'j01RenderContentSuccess',
        onError: 'j01RenderContentError',
        onTimeout: null,
        isPushState: true,
        id: null,
        dataURLName: null,
        preCallFunction: null,
        preventDefault: true,
        stopPropagation: false
    }, options);
    if (typeof(this.options.onSuccess) !== "string") {
        var t = typeof this.options.onSuccess;
        var msg = "j01LoadContent: onSuccess must be a string not " + t;
        alert(msg); // p01.checker.silence
    }
    if (typeof(this.options.onError) !== "string") {
        var t = typeof this.options.onError;
        var msg = "j01LoadContent: onError must be a string not " + t;
        alert(msg); // p01.checker.silence
    }
    if (typeof(this.options.onTimeout) !== "string" &&
        this.options.onTimeout !== null) {
        var t = typeof this.options.onTimeout;
        var msg = "j01LoadContent: onTimeout must be a string not " + t;
        alert(msg); // p01.checker.silence
    }
};

J01ContentLoader.prototype.process = function (self) {
    // load content from server via jsonrpc
    // process pre call function with context
    if (this.options.preCallFunction) {
        this.options.preCallFunction(self);
    }
    // get url and callback
    if (this.options.dataURLName !== null){
        // lookup data-url wihtout data- prefix
        var url = $(self).data(this.options.dataURLName);
        if (typeof url === 'undefined') {
            // lookup data-url including data- as attr
            var url = $(self).data(this.options.dataURLName);
        }
    }else{
        var url = $(self).attr('href');
    }
    // probably blocked by a href data marker
    var isPushState = $(self).attr('j01-history');
    if (typeof isPushState !== 'undefined' &&
        (isPushState == 'false' || isPushState == '0')){
        isPushState = false;
    } else if (typeof isPushState !== 'undefined' &&
        (isPushState == 'push' || isPushState == 'true' || isPushState == '1')){
        isPushState = true;
    } else {
        isPushState = this.options.isPushState;
    }
    var onSuccess = j01GetCallback(this.options.onSuccess);
    var onError = j01GetCallback(this.options.onError);
    var onTimeout = j01GetCallback(this.options.onTimeout, null);
    // load content
    j01LoadContentProcessor(url, onSuccess, onError, onTimeout, isPushState,
        this.options.id);
};


// -----------------------------------------------------------------------------
// jQuery api hooks
// -----------------------------------------------------------------------------
/**
 * j01LoadContent without delegation (not recommended)
 * this plugin does not re bind handlers for new loaded content
 */
(function ($) {
    $.fn.j01LoadContent = function (options) {
        // setup loader with given options
        var loader = new J01ContentLoader(options);
        return this.each(function () {
            // apply event handler to links
            $(this).click(function (event) {
                // process with our content loader
                loader.process(this);
                if (loader.options.preventDefault) {
                    event.preventDefault();
                }
                if (loader.options.stopPropagation) {
                    event.stopPropagation();
                }
                return false;
            });
        });
    };
})(jQuery);

/**
 * j01LoadContentOn uses delegation pattern (recommended)
 * This plugin uses the delegation pattern and works on new loaded content
 * You can use your own events. Normaly you can use the j01LoadContentOnClick
 * handler which uses this method with a predefined click event.
 */
(function ($) {
    $.fn.j01LoadContentOn = function (events, selector, options) {
        // apply delegated event handler
        var loader = new J01ContentLoader(options);
        return this.on(events, selector, function (event) {
            loader.process(this);
            if (loader.options.preventDefault) {
                event.preventDefault();
            }
            if (loader.options.stopPropagation) {
                event.stopPropagation();
            }
            return false;
        });
    };
})(jQuery);

/**
 * j01LoadContentOnClick uses delegation pattern (recommended)
 * this plugin uses the delegation pattern and works on new loaded content
 */
(function ($) {
    $.fn.j01LoadContentOnClick = function (selector, options) {
        if (typeof selector === "object") {
            // only options given, use default selector and adjust options
            options = selector;
            selector = 'a.j01LoadContentLink';
        } else if (typeof selector === "undefined") {
            // non argument given, use default selector
            selector = 'a.j01LoadContentLink';
        }
        // apply delegated event handler to click event
        return this.j01LoadContentOn('click', selector, options);
    };
})(jQuery);

// -----------------------------------------------------------------------------
// url and form helpers
// -----------------------------------------------------------------------------
function j01RemoveURLParam(url, param) {
    var urlparts = url.split('?'),
        prefix,
        pars,
        i;
    if (urlparts.length >= 2) {
        prefix = encodeURIComponent(param) + '=';
        pars = urlparts[1].split(/[&;]/g);
        for (i = 0; i < pars.length; i = i + 1) {
            if (pars[i].indexOf(prefix, 0) === 0) {
                pars.splice(i, 1);
            }
        }
        if (pars.length > 0) {
            return urlparts[0] + '?' + pars.join('&');
        } else {
            return urlparts[0];
        }
    } else {
        return url;
    }
}

function j01URLToArray(url, params) {
    if (typeof params === "undefined") {
        params = {};
    }
    var qString = null,
        strQueryString,
        i;
    if (typeof url !== "undefined" && url.indexOf("?") > -1) {
        strQueryString = url.substr(url.indexOf("?") + 1);
        qString = strQueryString.split("&");
    }
    if (qString === null) {
        if (typeof params !== "undefined") {
            return params;
        }else{
            return null;
        }
    }
    for (i = 0; i < qString.length; i = i + 1) {
        params[qString[i].split("=")[0]] = qString[i].split("=")[1];
    }
    return params;
}

(function ($) {
    /**
     * Serializes form data into a 'submittable' string. This method will
     * return string in the format: url?name1=value1&amp;name2=value2 or url
     */
    $.fn.j01FormToURL = function (url) {
        //hand off to jQuery.param for proper encoding
        var query = this.serialize();
        if (query) {
            return url +'?'+ query;
        } else {
            return url;
        }
    };

    /**
     * Taken from jquery.form and modified. We use an object instead of an
     * array as data container. This makes it possible to use the data with
     * JSON-RPC.
     *
     * j01FormToArray() gathers form element data into a data object which is a
     * collection of objects. Each object in the data object provides the field
     * name and the value. An example of an array for a simple login form might
     * be: {'login': 'jresig', 'password': 'secret'}
     */
    $.fn.j01FormToArray = function (handlerName) {
        var data = {},
            form,
            els,
            i,
            max,
            el,
            n,
            v,
            j,
            jmax,
            inputs,
            input;
        function add(n, v) {
            if (v !== null && typeof v !== 'undefined') {
                if (data[n]) {
                    var val = data[n];
                    if (val && val.constructor === Array) {
                        val.push(v);
                    } else {
                        val = [data[n]];
                        val.push(v);
                    }
                    data[n] = val;

                } else {
                    data[n] = v;
                }
            }
        }
        if (this.length === 0) {
            return data;
        }

        form = this[0];
        els = form.elements;
        if (!els) {
            return data;
        }
        for (i = 0, max = els.length; i < max; i = i + 1) {
            el = els[i];
            n = el.name;
            if (!n) {
                continue;
            }

            v = $.j01FieldValue(el);
            if (v && v.constructor === Array) {
                for (j = 0, jmax = v.length; j < jmax; j = j + 1) {
                    add(n, v[j]);
                }
            } else {
                if (v !== null && typeof v !== 'undefined') {
                    add(n, v);
                }
            }
        }

        if (form.clk) {
            // input type=='image' are not found in elements array! handle them here
            inputs = form.getElementsByTagName("input");
            for (i = 0, max = inputs.length; i < max; i = i + 1) {
                input = inputs[i];
                n = input.name;
                if (n && !input.disabled && input.type === "image" && form.clk === input) {
                    add(n, $(input).val());
                    add(n + '.x', form.clk_x);
                    add(n + '.y', form.clk_y);
                }
            }
        }
        if (handlerName) {
            add('j01FormHandlerName',  handlerName);
        }
        return data;
    };

    $.j01FieldValue = function(el) {
        var rCRLF = /\r?\n/g;
        var n = el.name,
            t = el.type,
            tag = el.tagName.toLowerCase();

        if (!n || el.disabled || t === 'reset' || t === 'button' ||
                ((t === 'checkbox' || t === 'radio') && !el.checked) ||
                ((t === 'submit' || t === 'image') && el.form && el.form.clk !== el) ||
                (tag === 'select' && el.selectedIndex === -1)) {
            return null;
        }

        if (tag === 'select') {
            var index = el.selectedIndex;
            if (index < 0) {
                return null;
            }
            var a = [];
            var ops = el.options;
            var one = (t === 'select-one');
            var max = (one ? index + 1 : ops.length);
            for (var i = (one ? index : 0); i < max; i++) {
                var op = ops[i];
                if (op.selected && !op.disabled) {
                    var v = op.value;
                    if (!v) {
                        // extra pain for IE...
                        v = (op.attributes && op.attributes.value && !(op.attributes.value.specified)) ? op.text : op.value;
                    }
                    if (one) {
                        return v;
                    }
                    a.push(v);
                }
            }
            return a;
        }
        return $(el).val().replace(rCRLF, '\r\n');
    };
})(jQuery);
