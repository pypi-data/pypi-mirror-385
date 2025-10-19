#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>

#include <gempyre.h>
#include <gempyre_graphics.h>
#include <gempyre_client.h>
#include <gempyre_utils.h>

#include <iostream>

namespace py = pybind11;


class RectF {
public:
    double x, y, width, height;
    operator Gempyre::Element::Rect() const {
        return Gempyre::Element::Rect{static_cast<int>(x), static_cast<int>(y), static_cast<int>(width), static_cast<int>(height)};
    }
};



static RectF rectF(const Gempyre::Element::Rect& r) {
    return RectF{ static_cast<double>(r.x), static_cast<double>(r.y), static_cast<double>(r.width), static_cast<double>(r.height) };
}


static std::optional<std::string> GempyreExtensionGet(Gempyre::Ui* ui, const std::string& callId, const std::unordered_map<std::string, std::string>& parameters) {
    std::unordered_map<std::string, std::any> params;
    for(const auto& [k, v] : parameters) {
        const auto any = GempyreUtils::json_to_any(v); // Not sure how well tested
        if(any)
            params.emplace(k, any);
         else {
            std::cerr << "Cannot make " << k << "->" << v << " to any" << std::endl;
            return std::nullopt;
        }
    }
    std::optional<std::any> ext =  ui->extension_get(callId, params);
    if(ext) {
        const auto result = GempyreUtils::to_json_string(*ext);
        if(result) {
            return result.value();
        }
    }
    return std::nullopt;
}

static void GempyreExtensionCall(Gempyre::Ui* ui, const std::string& callId, const std::unordered_map<std::string, std::string>& parameters) {
    std::unordered_map<std::string, std::any> params;
    for(const auto& [k, v] : parameters) {
        const auto any = GempyreUtils::json_to_any(v); // Not sure how well tested
        if(any)
            params.emplace(k, any);
         else {
            std::cerr << "Cannot make " << k << "->" << v << " to any" << std::endl;
            return;
        }
    }
    ui->extension_call(callId, params);
}

/*
static std::string findBrowser() {
    const auto pyclient = GempyreUtils::which("pyclient");
    if(!pyclient.empty()) {
        return pyclient;
    } else {
        try {
                const auto pyclient_browser = py::module::import("pyclient");
                const auto browser_path = pyclient_browser.attr("__file__");
                const auto browser = browser_path.cast<std::string>();

                if(!GempyreUtils::fileExists(browser))
                    return std::string();

                const auto sys = py::module::import("sys");
                const auto result = sys.attr("executable");
                return result.cast<std::string>() + " " + browser;

            } catch(...) {}
        }
    return std::string();
}
*/


using PyFileMap = std::map<std::string, std::string>;
#if 0 // not used
static Gempyre::Ui::FileMap to_map(PyFileMap&& map) {
    Gempyre::Ui::FileMap fmap;
    fmap.reserve(map.size());
    for(auto&& [k,v] : map) {
        fmap.push_back(std::make_pair(std::move(k), std::move(v)));
    }
    return fmap;
}
#endif
static Gempyre::Ui::FileMap to_map(const PyFileMap& map) {
    Gempyre::Ui::FileMap fmap;
    fmap.reserve(map.size());
    for(const auto& [k,v] : map) {
        fmap.push_back(std::make_pair(k, v));
    }
    return fmap;
}


PYBIND11_MODULE(_gempyre, m) {
    m.def("set_debug", &Gempyre::set_debug, py::arg("is_debug") = true);
    m.def("version", &Gempyre::version);
    m.def("html_file_launch_cmd", &GempyreUtils::html_file_launch_cmd); //is this the only function fom GempyreUtils? Therefore attached here

    py::class_<Gempyre::Event>(m, "Event")
            .def_readonly("element", &Gempyre::Event::element)
            .def_readonly("properties", &Gempyre::Event::properties)
            .def("has_true", [](Gempyre::Event* e, std::string_view key){
                return Gempyre::Event::has_true(e->properties, key); // this works a bit different than a C++ version
            })
            ;

    py::class_<RectF>(m, "Rect")
            .def(py::init<>())
            .def(py::init<double, double, double, double>())
            .def_readwrite("x", &RectF::x)
            .def_readwrite("y", &RectF::y)
            .def_readwrite("width", &RectF::width)
            .def_readwrite("height", &RectF::height)
            ;

    py::class_<Gempyre::Element>(m, "Element")
            .def(py::init<const Gempyre::Element&>())
            .def(py::init<Gempyre::Ui&, const std::string&>())
            .def(py::init<Gempyre::Ui&, const std::string, const std::string&, const Gempyre::Element&>())
            .def(py::init<Gempyre::Ui&, const std::string&, const Gempyre::Element&>())
            .def("ui", py::overload_cast<>(&Gempyre::Element::ui, py::const_))
            .def("ui", py::overload_cast<>(&Gempyre::Element::ui))
            .def("id", &Gempyre::Element::id)
            .def("subscribe", [](Gempyre::Element* el, const std::string& name, std::function<void(const Gempyre::Event& ev)> handler, const std::vector<std::string>& properties, const std::chrono::milliseconds& throttle = 0ms) {
                 return el->subscribe(name, [handler](const Gempyre::Event& ev) {
                     py::gil_scoped_acquire acquire; handler(ev);
                 }, properties, throttle);
                }, py::arg("name"), py::arg("handler"), py::arg("properties") = std::vector<std::string>{}, py::arg("throttle") = 0ms)
            .def("set_html", &Gempyre::Element::set_html)
            .def("set_attribute",  py::overload_cast<std::string_view, std::string_view>(&Gempyre::Element::set_attribute))
            .def("set_boolean_attribute",  py::overload_cast<std::string_view>(&Gempyre::Element::set_attribute))
            .def("remove_attribute", &Gempyre::Element::remove_attribute)
            .def("set_style", &Gempyre::Element::set_style)
            //.def("remove_style", &Gempyre::Element::removeStyle)
            .def("styles", &Gempyre::Element::styles)
            .def("attributes", &Gempyre::Element::attributes)
            .def("children", &Gempyre::Element::children)
            .def("values", &Gempyre::Element::values)
            .def("html", &Gempyre::Element::html)
            .def("remove", &Gempyre::Element::remove)
            .def("type", &Gempyre::Element::type)
            .def("rect", [](Gempyre::Element* el) {
                const auto r = el->rect();
                return r ? std::make_optional<RectF>(::rectF(*r)) :  std::nullopt;
                })
            .def("parent", &Gempyre::Element::parent);
                ;

    py::class_<Gempyre::Ui>(m, "Ui")
        .def(py::init([](
            const std::map<std::string, std::string>& map, 
            std::string_view html, 
            std::string_view title,
            int w, int h, int flags, const std::unordered_map<std::string, std::string>& params,int port, 
            std::string_view root) { 
                return std::make_unique<Gempyre::Ui>(to_map(map), html, title, w, h, flags, params, port, root);
            }),
             py::arg("filemap"),
             py::arg("index_html"),
             py::arg("title") = "",
             py::arg("width") = 620,
             py::arg("height") = 640,
             py::arg("flags") = 0,
             py::arg("ui_params") = std::unordered_map<std::string, std::string>{},
             py::arg("port") = Gempyre::Ui::UseDefaultPort,
             py::arg("root") = Gempyre::Ui::UseDefaultRoot)
        #if 0     
        .def(py::init<const Gempyre::Ui::FileMap&, const std::string&, const std::string&, int, int, 
         int, std::unordered_map<std::string, std::string>,
         unsigned int, const std::string& >(),
            py::arg("filemap"),
            py::arg("index_html"),
            py::arg("title") = "",
            py::arg("width") = 620,
            py::arg("height") = 640,
            py::arg("flags") = 0,
            py::arg("ui_params") = std::unordered_map<std::string, std::string>{},
            py::arg("port") = Gempyre::Ui::UseDefaultPort,
            py::arg("root") = Gempyre::Ui::UseDefaultRoot
            )
        #endif    
        .def(py::init([](const std::map<std::string, std::string>& map,
            std::string_view html,
            std::string_view browser,
            std::string_view browser_params,
            int port = static_cast<int>(Gempyre::Ui::UseDefaultPort),
            std::string_view root = Gempyre::Ui::UseDefaultRoot) {
                return std::make_unique<Gempyre::Ui>(to_map(map), html, browser, browser_params, port, root);
            }),
            py::arg("filemap"),
            py::arg("index_html"),
            py::arg("browser"),
            py::arg("browser_params"),
            py::arg("port") = Gempyre::Ui::UseDefaultPort,
            py::arg("root") = Gempyre::Ui::UseDefaultRoot)
        #if 0        
         .def(py::init<const Gempyre::Ui::FileMap&, const std::string&, const std::string&, const std::string&, unsigned int, const std::string& >(),
             py::arg("filemap"),
             py::arg("index_html"),
             py::arg("browser"),
             py::arg("browser_params"),
             py::arg("port") = Gempyre::Ui::UseDefaultPort,
             py::arg("root") = Gempyre::Ui::UseDefaultRoot
             )
        #endif     
        .def_readonly_static("UseDefaultPort", &Gempyre::Ui::UseDefaultPort)
        .def_readonly_static("UseDefaultRoot", &Gempyre::Ui::UseDefaultRoot)
        .def("run", &Gempyre::Ui::run, py::call_guard<py::gil_scoped_release>())
        .def("exit", &Gempyre::Ui::exit)
        //.def("close", [](Gempyre::Ui* ui) {
        //    PyErr_WarnEx(PyExc_DeprecationWarning, "use exit", 1); ui->close();})
        .def("on_exit", [](Gempyre::Ui* ui, std::function<void ()> onExitFunction = nullptr)-> auto {
            return ui->on_exit(onExitFunction ? [onExitFunction]() {
                py::gil_scoped_acquire acquire;
                return onExitFunction();
            } : static_cast<decltype(onExitFunction)>(nullptr));
        })
        .def("on_reload", [](Gempyre::Ui* ui, std::function<void ()> onReloadFunction = nullptr)-> auto {
        return ui->on_reload(onReloadFunction ? [onReloadFunction]() {
            py::gil_scoped_acquire acquire;
            return onReloadFunction();
        } : static_cast<decltype(onReloadFunction)>(nullptr));
        })
        .def("on_open", [](Gempyre::Ui* ui, std::function<void ()> onOpenFunction = nullptr)-> auto {
        return ui->on_open(onOpenFunction ? [onOpenFunction]() {
            py::gil_scoped_acquire acquire;
            return onOpenFunction();
        } : static_cast<decltype(onOpenFunction)>(nullptr));
        })
        .def("on_error", [](Gempyre::Ui* ui, std::function<void (const std::string& element, const std::string& info)> onErrorFunction = nullptr)-> auto {
            return ui->on_error(onErrorFunction ? [onErrorFunction](const std::string& element, const std::string& info) {
                py::gil_scoped_acquire acquire;
                return onErrorFunction(element, info);
            } : static_cast<decltype(onErrorFunction)>(nullptr));
        })
        .def("set_logging", &Gempyre::Ui::set_logging)
        .def("eval", &Gempyre::Ui::eval)
        .def("debug", &Gempyre::Ui::debug)
        .def("alert", &Gempyre::Ui::alert)
        .def("open", &Gempyre::Ui::open, py::arg("url"), py::arg("name") = "")
        .def("start_periodic", [](Gempyre::Ui* ui, const std::chrono::milliseconds& ms, const std::function<void ()>& f) {
            return ui->start_periodic(ms, [f]() {
                py::gil_scoped_acquire acquire;
                f();
            });
        })
        // When wrapping in fp (to enable GIL), there is no need: py::overload_cast<const std::chrono::milliseconds&, bool, const std::function<void (Gempyre::Ui::TimerId)>&>(&Gempyre::Ui::startTimer)
        .def("start_periodic_id", [](Gempyre::Ui* ui, const std::chrono::milliseconds& ms, const std::function<void (Gempyre::Ui::TimerId)>& f) {
            return ui->start_periodic(ms, [f](Gempyre::Ui::TimerId tid) {
                py::gil_scoped_acquire acquire;
                f(tid);
            });
        })
        .def("after", [](Gempyre::Ui* ui, const std::chrono::milliseconds& ms, const std::function<void ()>& f) {
        return ui->after(ms, [f]() {
            py::gil_scoped_acquire acquire;
            f();
            });
        })
        // When wrapping in fp (to enable GIL), there is no need: py::overload_cast<const std::chrono::milliseconds&, bool, const std::function<void (Gempyre::Ui::TimerId)>&>(&Gempyre::Ui::startTimer)
        .def("after_id", [](Gempyre::Ui* ui, const std::chrono::milliseconds& ms, const std::function<void (Gempyre::Ui::TimerId)>& f) {
        return ui->after(ms, [f](Gempyre::Ui::TimerId tid) {
            py::gil_scoped_acquire acquire;
            f(tid);
            });
        })
        .def("cancel_timer", &Gempyre::Ui::cancel_timer)
        .def("root", &Gempyre::Ui::root)
        .def("address_of", &Gempyre::Ui::address_of)
        .def("by_class", &Gempyre::Ui::by_class)
        .def("by_name", &Gempyre::Ui::by_name)
        .def("ping", &Gempyre::Ui::ping)
        .def("extension_get", &GempyreExtensionGet)
        .def("extension_call", &GempyreExtensionCall)
        .def("resource", &Gempyre::Ui::resource)
        .def("add_file_url", [](Gempyre::Ui* ui, const std::string& url, const std::string& file) {
                    return ui->add_file(url, file);
         })
        .def("begin_batch", &Gempyre::Ui::begin_batch)
        .def("end_batch", &Gempyre::Ui::end_batch)
        .def("set_timer__on_hold", &Gempyre::Ui::set_timer_on_hold)
        .def("is_timer__on_hold", &Gempyre::Ui::is_timer_on_hold)
        .def("device_pixel_ratio", &Gempyre::Ui::device_pixel_ratio)
        .def("available", &Gempyre::Ui::available)
        .def("add_data", &Gempyre::Ui::add_data)
        .def("flush", &Gempyre::Ui::flush)
        .def("resize", &Gempyre::Ui::resize)
        .def("set_title", &Gempyre::Ui::set_title)
        .def("set_application_icon", &Gempyre::Ui::set_application_icon)
        .def_static("to_file_map", &Gempyre::Ui::to_file_map)
            ;

        py::class_<Gempyre::CanvasElement, Gempyre::Element>(m, "CanvasElement")
                .def(py::init<const Gempyre::CanvasElement&>())
                .def(py::init<Gempyre::Ui&, const std::string&>())
                .def(py::init<Gempyre::Ui&, const std::string&, const Gempyre::Element&>())
                .def(py::init<Gempyre::Ui&, const Gempyre::Element&>())
                .def("add_image", [](Gempyre::CanvasElement* canvas, const std::string& url, const std::function<void (const std::string& id)> loaded = nullptr){
                    return canvas->add_image(url, [loaded](std::string_view id) {if(loaded) {py::gil_scoped_acquire acquire; loaded(std::string{id});}});})
                .def("paint_image", [](Gempyre::CanvasElement* el, const std::string& imageId, int x, int y, const RectF& clippingRect) {
                    el->paint_image(imageId, x, y, clippingRect);
                    }, py::arg("imageId"), py::arg("x"), py::arg("y"), py::arg("clippingRect") = RectF{0, 0, 0, 0})
                .def("paint_image_rect", [](Gempyre::CanvasElement* el, const std::string& imageId, const RectF& targetRect, const RectF& clippingRect) {
                    el->paint_image(imageId, targetRect, clippingRect);
                    }, py::arg("imageId"), py::arg("targetRect"), py::arg("clippingRect") = RectF{0, 0, 0, 0})
                .def("draw_commands", py::overload_cast<const Gempyre::CanvasElement::CommandList&>(&Gempyre::CanvasElement::draw))
                .def("draw_frame", py::overload_cast<const Gempyre::FrameComposer&>(&Gempyre::CanvasElement::draw))
                .def("draw_bitmap", py::overload_cast<const Gempyre::Bitmap&>(&Gempyre::CanvasElement::draw))
                .def("draw_bitmap_at", py::overload_cast<int, int, const Gempyre::Bitmap&>(&Gempyre::CanvasElement::draw))
                .def("erase", &Gempyre::CanvasElement::erase, py::arg("resized") = false)
                .def("draw_completed", [](Gempyre::CanvasElement* canvas, std::function<void ()> drawCallback)-> void {
                    canvas->draw_completed(drawCallback ? [drawCallback]() {
                        py::gil_scoped_acquire acquire;
                        drawCallback();
                    } : static_cast<decltype(drawCallback)>(nullptr));
                })
                
                ;
        m.def("color_rgba_clamped", &Gempyre::Color::rgba_clamped, py::arg("r"), py::arg("g"), py::arg("b"), py::arg("a") = 0xFF);
        m.def("color_rgba", py::overload_cast<uint32_t, uint32_t, uint32_t, uint32_t>(&Gempyre::Color::rgba), py::arg("r"), py::arg("g"), py::arg("b"), py::arg("a") = 0xFF);
        m.def("color_rgba_string", py::overload_cast<uint32_t>(&Gempyre::Color::rgba));
        m.def("color_rgb_string", py::overload_cast<uint32_t>(&Gempyre::Color::rgb));
        m.def("color_r", &Gempyre::Color::r);
        m.def("color_g", &Gempyre::Color::g);
        m.def("color_b", &Gempyre::Color::b);
        m.def("color_alpha", &Gempyre::Color::alpha);
        m.attr("Black") = py::int_(Gempyre::Color::Black);
        m.attr("White") = py::int_(Gempyre::Color::White);
        m.attr("Black") = py::int_(Gempyre::Color::Black);
        m.attr("Red") = py::int_(Gempyre::Color::Red);
        m.attr("Green") = py::int_(Gempyre::Color::Green);
        m.attr("Blue") = py::int_(Gempyre::Color::Blue);
        m.attr("Yellow") = py::int_(Gempyre::Color::Magenta);
        m.attr("Lime") = py::int_(Gempyre::Color::Lime);
        m.attr("Cyan") = py::int_(Gempyre::Color::Cyan);
        m.attr("Fuchsia") = py::int_(Gempyre::Color::Fuchsia);
        m.attr("Aqua") = py::int_(Gempyre::Color::Aqua);
        m.attr("Magenta") = py::int_(Gempyre::Color::Magenta);

        py::class_<Gempyre::Bitmap>(m, "Bitmap")
                .def(py::init<int, int>())
                .def(py::init<const Gempyre::Bitmap&>())
                .def(py::init<const std::vector<uint8_t>&>())
                .def("create", &Gempyre::Bitmap::create)
                .def("clone", &Gempyre::Bitmap::clone)
                .def("set_pixel", &Gempyre::Bitmap::set_pixel)
                .def("set_alpha", &Gempyre::Bitmap::set_alpha)
                .def("pixel", &Gempyre::Bitmap::pixel)
                .def("width", &Gempyre::Bitmap::width)
                .def("height", &Gempyre::Bitmap::height)
                .def("draw_rect", [](Gempyre::Bitmap* g, const RectF& r, Gempyre::Color::type c) {g->draw_rect(r, c);})
                .def("merge_at", py::overload_cast<int, int, const Gempyre::Bitmap&>(&Gempyre::Bitmap::merge))
                .def("merge", py::overload_cast<const Gempyre::Bitmap&>(&Gempyre::Bitmap::merge))
                .def("swap", &Gempyre::Bitmap::swap)
                .def("clip", &Gempyre::Bitmap::clip)
                .def("empty", &Gempyre::Bitmap::empty)
                .def("tile", &Gempyre::Bitmap::empty)
                .def("png_image", &Gempyre::Bitmap::png_image)
                .def("set_data", [](Gempyre::Bitmap* g, const std::vector<Gempyre::Color::type>& bytes, size_t offset = 0)-> bool {
                    return g->set_data(bytes, offset); // set_data should be fixed to take byte spans
                })
                .def_static("pix", &Gempyre::Bitmap::pix, py::arg("r"), py::arg("g"), py::arg("b"), py::arg("a") = 0xFF)
                ;
        
        py::class_<Gempyre::FrameComposer>(m, "FrameComposer")
                .def(py::init<>())
                .def(py::init<Gempyre::CanvasElement::CommandList&>())
                .def(py::init<const Gempyre::FrameComposer&>())
                .def("stroke_rect", [](Gempyre::FrameComposer* fc, const RectF& r) {fc->stroke_rect(r);})
                .def("clear_rect", [](Gempyre::FrameComposer* fc, const RectF& r) {fc->clear_rect(r);})
                .def("fill_rect", [](Gempyre::FrameComposer* fc, const RectF& r) {fc->fill_rect(r);})
                .def("fill_text", &Gempyre::FrameComposer::fill_text)
                .def("stroke_text", &Gempyre::FrameComposer::stroke_text)
                .def("arc", &Gempyre::FrameComposer::arc)
                .def("ellipse", &Gempyre::FrameComposer::ellipse)
                .def("begin_path", &Gempyre::FrameComposer::begin_path)
                .def("close_path", &Gempyre::FrameComposer::close_path)
                .def("line_to", &Gempyre::FrameComposer::line_to)
                .def("move_to", &Gempyre::FrameComposer::move_to)
                .def("bezier_curve_to", &Gempyre::FrameComposer::bezier_curve_to)
                .def("quadratic_curve_to", &Gempyre::FrameComposer::quadratic_curve_to)
                .def("arc_to", &Gempyre::FrameComposer::arc_to)
                .def("rect", [](Gempyre::FrameComposer* fc, const RectF& r) {fc->rect(r);})
                .def("stroke", &Gempyre::FrameComposer::stroke)
                .def("fill", &Gempyre::FrameComposer::fill)
                .def("fill_style", &Gempyre::FrameComposer::fill_style)
                .def("stroke_style", &Gempyre::FrameComposer::stroke_style)
                .def("line_width", &Gempyre::FrameComposer::line_width)
                .def("font", &Gempyre::FrameComposer::font)
                .def("text_align", &Gempyre::FrameComposer::text_align)
                .def("save", &Gempyre::FrameComposer::save)
                .def("restore", &Gempyre::FrameComposer::restore)
                .def("rotate", &Gempyre::FrameComposer::rotate)
                .def("translate", &Gempyre::FrameComposer::translate)
                .def("scale", &Gempyre::FrameComposer::scale)
                .def("text_baseline", &Gempyre::FrameComposer::text_baseline)
                .def("draw_image", py::overload_cast<std::string_view, double, double>(&Gempyre::FrameComposer::draw_image))
                .def("draw_image_rect", [](Gempyre::FrameComposer* fc, const std::string& id, const RectF& r) {fc->draw_image(id, r);})
                .def("draw_image_clip", [](Gempyre::FrameComposer* fc, const std::string& id, const RectF& c, const RectF& r){fc->draw_image(id, c, r);})
                .def("composed", &Gempyre::FrameComposer::composed)
                ;
    
        py::class_<Gempyre::Dialog>(m, "Dialog")
            .def(py::init())
            
            .def("open_file_dialog", [](Gempyre::Dialog* self, const std::string& caption, const std::string& root, const std::vector<std::tuple<std::string, std::vector<std::string>>>& filter = {})->std::optional<std::string> {
                (void) self;
                py::gil_scoped_acquire acquire;
                return Gempyre::Dialog::open_file_dialog(caption, root, filter);
            }, py::arg("caption")="", py::arg("root")="", py::arg("filter")=Gempyre::Dialog::Filter())
            
            .def("open_files_dialog", [](Gempyre::Dialog* self, const std::string& caption, const std::string& root, const std::vector<std::tuple<std::string, std::vector<std::string>>>& filter = {})->std::optional<std::vector<std::string>> {
                (void) self;
                py::gil_scoped_acquire acquire;
                return Gempyre::Dialog::open_files_dialog(caption, root, filter);
            }, py::arg("caption")="", py::arg("root")="", py::arg("filter")=Gempyre::Dialog::Filter())
            
            .def("open_dir_dialog", [](Gempyre::Dialog* self, const std::string& caption, const std::string& root)->std::optional<std::string> {
                (void) self;
                py::gil_scoped_acquire acquire;
                return Gempyre::Dialog::open_dir_dialog(caption, root);
            }, py::arg("caption")="", py::arg("root")="")
            
            .def("save_file_dialog", [](Gempyre::Dialog* self, const std::string& caption, const std::string& root, const std::vector<std::tuple<std::string, std::vector<std::string>>>& filter = {})->std::optional<std::string> {
                (void) self;
                py::gil_scoped_acquire acquire;
                return Gempyre::Dialog::save_file_dialog(caption, root, filter);
            }, py::arg("caption")="", py::arg("root")="", py::arg("filter")=Gempyre::Dialog::Filter())
            ;
}
