export const name = "quillmodules";

// import 'quill-mention/autoregister';
import { Mention, MentionBlot } from 'quill-mention';
import Quill from 'quill-next';
import QuillNextEditor from "quill-next-react";
export { QuillNextEditor };
import QuillImageDropAndPaste from 'quill-image-drop-and-paste';
import BlotFormatter from '@enzedonline/quill-blot-formatter2';
import htmlEditButton from "quill-html-edit-button";
// import QuillBetterTable from "quill-better-table";
import React from 'react';
import { RegisterImportPool } from "./Base";

import "@enzedonline/quill-blot-formatter2/dist/css/quill-blot-formatter2.css"; // align styles

const TableNext = Quill.import("modules/table");


class TableMenu {
    constructor(params, quill, options) {
        const tableModule = quill.getModule("table");
        this.params = params;
        this.menuItems = params.menuItems;
        this.quill = quill;
        this.options = options;

        this.showMenu()

        this.destroyHandler = this.destroy.bind(this);

        document.addEventListener("click", this.destroyHandler);
    }

    showMenu() {
        const dn = this.domNode = document.createElement("div");
        dn.style.position = "absolute";
        dn.style.left = `${this.params.left}px`;
        dn.style.top = `${this.params.top}px`;

        const createItem = (desc) => {
            const node = document.createElement("div");
            node.classList.add("l-span-clickable");

            const iconSpan = document.createElement("span");
            if (desc.iconClass) {
                const i = document.createElement("i");
                i.classList.add("pi");
                i.classList.add(desc.iconClass);
                iconSpan.appendChild(i)
            } else iconSpan.innerText = desc.icon;
            iconSpan.style.width = "3ch";
            iconSpan.style.display = "inline-block";
            iconSpan.style["text-align"] = "center";

            const textSpan = document.createElement("span");
            textSpan.innerText = desc.text;

            node.appendChild(iconSpan);
            node.appendChild(textSpan);

            node.addEventListener("click", desc.handler);
            return node;
        }

        Object.values(this.menuItems).forEach((desc) => {
            dn.appendChild(createItem(desc));
        });

        document.body.appendChild(dn);
    }

    destroy() {
        this.domNode.remove();
        document.removeEventListener("click", this.destroyHandler);
        return null;
    }
}


class Table extends TableNext {
    constructor(quill, options) {
        super(quill, options);

        quill.root.addEventListener("contextmenu", (event) => {
            const [table] = this.getTable();
            if (table === null) return;

            event.preventDefault();
            if (this.tableMenu)
                this.tableMenu = this.tableMenu.destroy();

            this.tableMenu = new TableMenu({
                menuItems: this.getMenuItems(options.i18n),
                left: event.pageX,
                top: event.pageY,
            }, quill, options)
        });
    }

    getMenuItems(i18n) {
        return {
            insertColumnLeft: {
                text: i18n.t("Insert column left"),
                icon: "⭰",
                handler: () => {
                    this.quill.focus();
                    this.insertColumnLeft();
                },
            },
            insertColumnRight: {
                text: i18n.t("Insert column right"),
                icon: "⭲",
                handler: () => {
                    this.quill.focus();
                    this.insertColumnRight();
                },
            },
            insertRowAbove: {
                text: i18n.t("Insert row above"),
                icon: "⭱",
                handler: () => {
                    this.quill.focus();
                    this.insertRowAbove();
                },
            },
            insertRowBelow: {
                text: i18n.t("Insert row below"),
                icon: "⭳",
                handler: () => {
                    this.quill.focus();
                    this.insertRowBelow();
                },
            },
            deleteColumn: {
                text: i18n.t("Delete column"),
                iconClass: "pi-delete-left",
                handler: () => {
                    this.quill.focus();
                    this.deleteColumn();
                },
            },
            deleteRow: {
                text: i18n.t("Delete row"),
                iconClass: "pi-eraser",
                handler: () => {
                    this.quill.focus();
                    this.deleteRow();
                },
            },
            deleteTable: {
                text: i18n.t("Delete table"),
                iconClass: "pi-trash",
                handler: () => {
                    this.quill.focus();
                    this.deleteTable();
                },
            },
        }
    }
}

Quill.register('modules/table', Table);
Quill.register('modules/imageDropAndPaste', QuillImageDropAndPaste);
Quill.register('modules/blotFormatter2', BlotFormatter);
Quill.register({"blots/mention": MentionBlot, "modules/mention": Mention});
Quill.register('modules/htmlEditButton', htmlEditButton);
// Quill.register('modules/better-table', QuillBetterTable);
// Quill.register(SoftLineBreakBlot);

const QuillImageData = QuillImageDropAndPaste.ImageData;

let ex; const exModulePromises = ex = {
    queryString:  import(/* webpackChunkName: "queryString_quillmodules" */"query-string"),
};RegisterImportPool(ex);


export const quillLoad = (elem, quill) => {
    const value = elem.getValue();
    if (elem.state.plain) {
        quill.setText(value || "");
    } else {
        quill.clipboard.dangerouslyPasteHTML(value);
    }
}


export const onTextChange = (elem, e) => {
    // console.log("onTextChange", e);
    // cleans up the trailing new line (\n)
    const plainValue = e.textValue.slice(0, -1);
    let value = (elem.state.plain ? plainValue : e.htmlValue ) || "";

    // When an image is seleted and on CTRL+S, before deselecting
    // the image blotFormatter2 resets the --resize-width property;
    // some transitional state. Clean it out.
    // value = value.replace(/--resize-width:\s*0px;?/g, "");
    // better yet instead of cleaning it out, replace the value with img.width
    // if (!elem.state.plain && e.source !== "user") {
    //     const el = document.createElement("div");
    //     el.innerHTML = value;
    //     el.querySelectorAll("img[width]").forEach(img => {
    //         const widthAttr = img.getAttribute("width").split("px")[0];
    //         if (!widthAttr) return;
    //
    //         const parent = img.closest("[style]");
    //         if (parent) {
    //             const cssWidth = parent.style.getPropertyValue("--resize-width");
    //             if (cssWidth === "0px" || cssWidth === "") {
    //                 parent.style.setProperty("--resize-width", widthAttr + "px");
    //             }
    //         }
    //     })
    //     value = el.innerHTML;
    // }
    //
    // console.log(e.source, value);
    // if (!elem.state.plain) {
    //     const el = document.createElement("div");
    //     el.innerHTML = value;
    //     el.querySelectorAll("img").forEach(img => {
    //       // Prefer style.width, fallback to attribute
    //       let w = img.style.width || img.getAttribute("width");
    //       if (w) {
    //         w = w.replace("px", "");
    //         img.setAttribute("width", w);
    //         img.style.width = w + "px"; // keep inline for display
    //       }
    //     });
    //     value = el.innerHTML;
    // }

    // if (e.source === "user") elem.update({[elem.dataKey]: value});
    elem.update({[elem.dataKey]: value});
    // elem.setState({})
    // elem.setState({});
    // elem.updateValue(value);
}


export const getQuillModules = (
    APP, silentFetch, signal, mentionValues, i18n, elem, hasToolbar = true
) => {
    const toolbarID = `l-ql-toolbar-${elem.props.elem.name}`;
    const modules = {
        toolbar: `#${toolbarID}`,
        mention: quillMention({
            silentFetch: silentFetch,
            signal: signal,
            mentionValues: mentionValues,
        }),
        blotFormatter2: {
            debug: true,
            resize: {
                useRelativeSize: true,
            },
        },
        table: {i18n},
        // "better-table": {
        //     operationMenu: {
        //         // items: {
        //         //     mergeCells: {
        //         //         text: i18n.t("Merge cells"),
        //         //     }
        //         // },
        //     }
        // }
    }
    if (hasToolbar) {
        modules.htmlEditButton = {
            msg: i18n.t('Edit HTML here, when you click "OK" the quill editor\'s contents will be replaced'),
            prependSelector: "div#raw-editor-container",
            okText: i18n.t("Ok"),
            cancelText: i18n.t("Cancel"),
            buttonTitle: i18n.t("Show HTML source"),
            // editorModules: {
            //     clipboard: {
            //         matchers: [
            //             ["BR", brMatcher],
            //         ]
            //     }
            // }
        }
    }
    if (APP.state.site_data.installed_plugins.includes('uploads'))
        modules.imageDropAndPaste = {handler: imageHandler(elem)};
    modules.keyboard = {
        bindings: {
            // ...QuillBetterTable.keyboardBindings,
            home: {
                key: "Home",
                handler: function (range, context) {
                    const { quill } = elem;
                    let [line, offset] = quill.getLine(range.index);
                    if (line && line.domNode.tagName === "LI") {
                      // Move to the start of text inside the list item
                      quill.setSelection(line.offset(quill.scroll), 0, "user");
                      return false; // stop default browser behavior
                    }
                    return true;
                },
            },
            // shiftReturn: {
            //     key: "Enter",
            //     shiftKey: true,
            //     handler: function (range, context) {
            //         const { quill } = elem;
            //         // const currentLeaf = quill.getLeaf(range.index)[0];
            //         // const nextLeaf = quill.getLeaf(range.index + 1)[0];
            //         // quill.insertEmbed(range.index, "softbreak", true, Quill.sources.USER);
            //         // // Insert a second break if:
            //         // // At the end of the editor, OR next leaf has a different parent (<p>)
            //         // if (nextLeaf === null || currentLeaf.parent !== nextLeaf.parent) {
            //         //   quill.insertEmbed(range.index, "softbreak", true, Quill.sources.USER);
            //         // }
            //         // // Now that we've inserted a line break, move the cursor forward
            //         // quill.setSelection(range.index + 4, Quill.sources.SILENT);
            //         // return false;
            //         var nextChar = quill.getText(range.index + 1, 1)
            //         var ee = quill.insertEmbed(range.index, 'break', true, 'user');
            //         if (nextChar.length == 0) {
            //           // second line break inserts only at the end of parent element
            //           var ee = quill.insertEmbed(range.index, 'break', true, 'user');
            //         }
            //         quill.setSelection(range.index + 1, Quill.sources.SILENT);
            //         return false;
            //     },
            // }
        }
    }
    // modules.clipboard = {
    //     matchers: [
    //         ["BR", brMatcher],
    //     ],
    // }

    if (!hasToolbar) delete modules.toolbar;

    const meta = {toolbarID};

    return {modules, meta};
}


export const changeDelta = (elem) => {
    return (delta, oldContents, source) => {
        // copied from primereact/components/lib/editor/Editor.js
        const quill = elem.quill;
        let firstChild = quill.container.children[0];
        let html = firstChild ? firstChild.innerHTML : null;
        let text = quill.getText();

        if (html === '<p><br></p>') {
            html = null;
        }

        // GitHub primereact #2271 prevent infinite loop on clipboard paste of HTML
        if (source === 'api') {
            const htmlValue = quill.container.children[0];
            const editorValue = document.createElement('div');

            editorValue.innerHTML = elem.getValue() || '';

            // this is necessary because Quill rearranged style elements
            if (elem.ex.prUtils.DomHandler.isEqualElement(htmlValue, editorValue)) {
                return;
            }
        }

        onTextChange(elem, {
            htmlValue: html,
            textValue: text,
            delta: delta,
            source: source
        });
    }
}


export const overrideImageButtonHandler = (quill) => {
    quill.getModule('toolbar').addHandler('image', (clicked) => {
        if (clicked) {
            let fileInput;
            // fileInput = quill.container.querySelector('input.ql-image[type=file]');
            // if (fileInput == null) {
                fileInput = document.createElement('input');
                fileInput.setAttribute('type', 'file');
                fileInput.setAttribute('accept', 'image/png, image/gif, image/jpeg, image/bmp, image/x-icon');
                fileInput.classList.add('ql-image');
                fileInput.addEventListener('change', (e) => {
                    const files = e.target.files;
                    let file;
                    if (files.length > 0) {
                        file = files[0];
                        const type = file.type;
                        const reader = new FileReader();
                        reader.onload = (e) => {
                            const dataURL = e.target.result;
                            imageHandler({quill})(
                                dataURL,
                                type,
                                new QuillImageData(dataURL, type, file.name)
                            );
                            fileInput.value = '';
                        }
                        reader.readAsDataURL(file);
                    }
                })
            // }
            fileInput.click();
        }
    })
}

export const imageHandler = (elem) => {
    return (imageDataURL, type, imageData) => {
        const quill = elem.quill;
        let index = (quill.getSelection() || {}).index;
        if (index === undefined || index < 0) index = quill.getLength();
        quill.insertEmbed(index, 'image', imageDataURL);
    }

    // const imageEl = quill.root.querySelector(`img[src="${imageDataURL}"]`);
    // Set default height
    // imageEl.setAttribute("height", window.App.URLContext.root.chInPx.offsetHeight * 20);
}

export const quillMention = ({silentFetch, signal, mentionValues}) => {
    function mentionSource(searchTerm, renderList, mentionChar) {
        if (searchTerm.length === 0) {
            let values = mentionValues[mentionChar];
            renderList(values, searchTerm);
        } else {
            ex.resolve(['queryString']).then(({queryString}) => {
                silentFetch({path: `suggestions?${queryString.default.stringify({
                    query: searchTerm, trigger: mentionChar})}`, signal: signal})
                .then(data => renderList(data.suggestions, searchTerm));
            });
        }
    }

    return {
        allowedChars: /^[A-Za-z0-9\s]*$/,
        mentionDenotationChars: window.App.state.site_data.suggestors,
        source: mentionSource,
        listItemClass: "ql-mention-list-item",
        mentionContainerClass: "ql-mention-list-container",
        mentionListClass: "ql-mention-list",
        dataAttributes: ["value", "link", "title", "denotationChar"],
    }
}

const quillToolbarHeaderTemplate = <React.Fragment>
    <span className="ql-formats">
        <select className='ql-header' defaultValue='0'>
            <option value='1'>Header 1</option>
            <option value='2'>Header 2</option>
            <option value='3'>Header 3</option>
            <option value='4'>Header 4</option>
            <option value='0'>Normal</option>
        </select>
        <select className='ql-font'>
            <option defaultValue={true}></option>
            <option value='serif'></option>
            <option value='monospace'></option>
        </select>
    </span>
    <span className="ql-formats">
        <select className="ql-size">
            <option value="small"></option>
            <option defaultValue={true}></option>
            <option value="large"></option>
            <option value="huge"></option>
        </select>
    </span>
    <span className="ql-formats">
        <button className="ql-script" value="sub"></button>
        <button className="ql-script" value="super"></button>
    </span>
    <span className="ql-formats">
        <button type='button' className='ql-bold' aria-label='Bold'></button>
        <button type='button' className='ql-italic' aria-label='Italic'></button>
        <button type='button' className='ql-underline' aria-label='Underline'></button>
    </span>
    <span className="ql-formats">
        <select className='ql-color'></select>
        <select className='ql-background'></select>
    </span>
    <span className="ql-formats">
        <button type='button' className='ql-list' value='ordered' aria-label='Ordered List'></button>
        <button type='button' className='ql-list' value='bullet' aria-label='Unordered List'></button>
        <select className='ql-align'>
            <option defaultValue={true}></option>
            <option value='center'></option>
            <option value='right'></option>
            <option value='justify'></option>
        </select>
    </span>
    <span className="ql-formats">
        <button type='button' className='ql-link' aria-label='Insert Link'></button>
        <button type='button' className='ql-image' aria-label='Insert Image'></button>
        <button type='button' className='ql-code-block' aria-label='Insert Code Block'></button>
    </span>
    <span className="ql-formats">
        <button type='button' className='ql-clean' aria-label='Remove Styles'></button>
    </span>
</React.Fragment>

export const invokeRefInsert = (elem) => {
    const { APP } = elem.props.urlParams.controller;
    const { URLContext } = APP;
    let index = (elem.quill.getSelection() || {}).index;
    if (index === undefined || index < 0)
        index = elem.quill.getLength();
    URLContext.actionHandler.runAction({
        action_full_name: URLContext.actionHandler.findUniqueAction("insert_reference").full_name,
        actorId: "about.About",
        response_callback: (data) => {
            if (data.success)
                elem.quill.insertText(index, data.message);
        }
    });
}

export const refInsert = (elem) => {
    if (!elem.c.APP.state.site_data.installed_plugins.includes('memo'))
        return null;
    return <span className="ql-formats">
        <button type='button'
            onClick={(e) => invokeRefInsert(elem)}
            aria-label='Open link dialog'>
            <i className="pi pi-link"></i></button>
    </span>
}

const commonHeader = (elem) => {
    return <>
        {quillToolbarHeaderTemplate}
        {refInsert(elem)}
        {
        <span className="ql-formats">
            <button type="button"
                onClick={e => {
                    const title = elem.ex.i18n.t("rows x columns");
                    const rows_text = elem.ex.i18n.t("Rows");
                    const columns_text = elem.ex.i18n.t("Columns");
                    const ok = (holder) => {
                        const rows = parseInt(holder.context.data[rows_text]);
                        const cols = parseInt(holder.context.data[columns_text]);
                        const t = elem.quill.getModule("table");
                        elem.quill.focus();
                        t.insertTable(rows, cols);

                        const { factory, id } = holder.current.root.props;
                        factory.remove(id);
                    }
                    const ctx = elem.props.urlParams.controller;
                    ctx.APP.dialogFactory.createParamDialog(ctx, {
                        [rows_text]: "IntegerFieldElement",
                        [columns_text]: "IntegerFieldElement",
                    }, title, ok);
                }}>
                <i className="pi pi-table"></i></button>
        </span>
        }
    </>
}

export const quillToolbar = {
    header: quillToolbarHeaderTemplate,
    commonHeader: commonHeader,
}
