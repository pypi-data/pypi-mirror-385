// CKEditor configuration for Django Blog Package
CKEDITOR.editorConfig = function(config) {
    // Define the toolbar groups configuration
    config.toolbarGroups = [
        { name: 'document', groups: ['mode', 'document', 'doctools'] },
        { name: 'clipboard', groups: ['clipboard', 'undo'] },
        { name: 'editing', groups: ['find', 'selection', 'spellchecker'] },
        { name: 'forms' },
        '/',
        { name: 'basicstyles', groups: ['basicstyles', 'cleanup'] },
        { name: 'paragraph', groups: ['list', 'indent', 'blocks', 'align', 'bidi'] },
        { name: 'links' },
        { name: 'insert' },
        '/',
        { name: 'styles' },
        { name: 'colors' },
        { name: 'tools' },
        { name: 'others' },
        { name: 'about' }
    ];

    // Remove some buttons provided by the standard plugins
    config.removeButtons = 'Save,NewPage,Preview,Print,Templates,Cut,Copy,Paste,PasteText,PasteFromWord,Find,Replace,SelectAll,Scayt,Form,Checkbox,Radio,TextField,Textarea,Select,Button,ImageButton,HiddenField,CreateDiv,BidiLtr,BidiRtl,Language,Flash,PageBreak,Iframe,Font,FontSize,Styles';

    // Set the most common block elements
    config.format_tags = 'p;h1;h2;h3;h4;h5;h6;pre;address;div';

    // Simplify the dialog windows
    config.removeDialogTabs = 'image:advanced;link:advanced';

    // Configure image upload
    config.filebrowserUploadUrl = '/ckeditor/upload/';
    config.filebrowserUploadMethod = 'form';

    // Configure allowed content
    config.allowedContent = true;

    // Enable content filtering
    config.autoParagraph = false;

    // Configure styles
    config.stylesSet = [
        { name: 'Heading 2', element: 'h2' },
        { name: 'Heading 3', element: 'h3' },
        { name: 'Heading 4', element: 'h4' },
        { name: 'Code Block', element: 'pre' },
        { name: 'Blockquote', element: 'blockquote' },
        { name: 'Highlight', element: 'span', attributes: { 'class': 'highlight' } }
    ];

    // Configure code snippet plugin if available
    if (typeof CKEDITOR.plugins.get('codesnippet') !== 'undefined') {
        config.codeSnippet_theme = 'monokai_sublime';
    }

    // Set default height
    config.height = 400;

    // Configure language
    config.language = 'en';

    // Configure extra plugins
    config.extraPlugins = 'codesnippet,image2,uploadimage';

    // Configure image upload
    config.imageUploadUrl = '/ckeditor/upload/';

    // Configure file browser
    config.filebrowserBrowseUrl = '/ckeditor/browse/';

    // Configure contents CSS to match blog styling
    config.contentsCss = [
        'https://cdn.tailwindcss.com',
        '/static/blog/css/custom.css'
    ];

    // Configure autoGrow plugin
    config.autoGrow_minHeight = 400;
    config.autoGrow_maxHeight = 800;
    config.autoGrow_bottomSpace = 50;

    // Configure word count
    config.wordcount = {
        showParagraphs: false,
        showWordCount: true,
        showCharCount: true,
        countSpacesAsChars: false,
        countHTML: false
    };

    // Configure paste filter
    config.pasteFilter = 'p;br;strong;em;u;ol;ul;li;a[href];img[src,alt];h1;h2;h3;h4;h5;h6;blockquote;pre;code;table;thead;tbody;tr;th;td';

    // Configure link target
    config.linkDefaultTarget = '_blank';
};

// Custom CKEditor styles for blog content
if (typeof CKEDITOR !== 'undefined') {
    CKEDITOR.stylesSet.add('blog_styles', [
        // Block styles
        { name: 'Lead Paragraph', element: 'p', attributes: { 'class': 'text-xl text-gray-700 mb-6' } },
        { name: 'Small Text', element: 'p', attributes: { 'class': 'text-sm text-gray-500' } },

        // Inline styles
        { name: 'Highlight', element: 'span', attributes: { 'class': 'bg-yellow-200 px-1' } },
        { name: 'Code Inline', element: 'code', attributes: { 'class': 'bg-gray-100 text-red-600 px-2 py-1 rounded text-sm' } },

        // List styles
        { name: 'Checklist Item', element: 'li', attributes: { 'class': 'flex items-center space-x-2' } },

        // Table styles
        { name: 'Striped Table', element: 'table', attributes: { 'class': 'min-w-full divide-y divide-gray-200' } },
        { name: 'Table Header', element: 'th', attributes: { 'class': 'px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider' } },
        { name: 'Table Cell', element: 'td', attributes: { 'class': 'px-6 py-4 whitespace-nowrap text-sm text-gray-900' } }
    ]);
}
