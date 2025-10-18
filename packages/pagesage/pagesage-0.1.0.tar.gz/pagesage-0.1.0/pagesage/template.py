from pygments.formatters import HtmlFormatter

def assemble(content, header="", footer=""):
    html = default.replace("%content%", content)
    html = html.replace("%header%", header)
    html = html.replace("%footer%", footer)
    return html

default = f"""
<!DOCTYPE HTML>
<html>

  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <link rel="shortcut icon" type="image/png" href="/favicon.ico"/>
    <style type="text/css">
      html {{
        font-family       : arial, verdana;
      }}
      body {{
        color             : #ddd;
        background-color  : #000;
        margin            : 0 10px;
        padding           : 0;
      }}
      p {{
        line-height       : 150%;
      }}
      a {{
        color             : #6af;
        text-decoration   : none;
      }}
      a:hover {{
        text-decoration   : underline;
      }}
  
      table {{
        font-family: mono;
        font-size         : 80%;
        border-width      : 1px;
        border-color      : #999;
        border-collapse   : collapse;
        margin            : 10px 0;
      }}
      table th {{
        border-width      : 1px;
        padding           : 8px;
        border-style      : solid;
      }}
      table td {{
        border-width      : 1px;
        padding           : 8px;
        border-style      : solid;
      }}
  
      code {{
        padding           : 2px;
        margin            : 0px;
      }}
      .codehilite {{
        border-style      : solid;
        border-width      : 1px;
        border-color      : #999;
        border-radius     : 5px;
        padding           : 6px;
        overflow          : auto;
      }}
      .codehilite code {{
        padding           : 0px;
        margin            : 0px;
      }}

      blockquote {{
        padding-left      : 5px;
        border-color      : #999;
        border-style      : solid;
        border-width      : 0 0 0 5px;
      }}
  
      #wrapper {{
        width             : 100%;
        margin            : 0 auto;
        padding           : 0;
      }}

      #toc {{
        font-size         : 90%;
        min-width         : 50px;
        background-color  : #111;
        margin            : 0 10px 0 0;
        padding           : 0 1em 0 1em;
        border-style      : solid;
        border-width      : 1px 1px 1px 0;
        border-color      : #999;
        border-radius     : 3px;
        float             : left;
      }}
      #toc ul {{
        list-style-type   : none;
        padding           : 0;
      }}
      #toc li {{
        border-style      : solid;
        border-width      : 0 0 0 1px;
        padding           : 0 0 0 1em;
        margin            : 0;
      }}

      #markdown {{
        margin            : 10px 10px 10px 10px;
        padding           : 10px;
        border-style      : solid;
        border-width      : 1px;
        border-radius     : 3px;
        overflow          : hidden;
        min-height        : 100%;
      }}
      #markdown h1 {{
        border-style      : solid;
        border-width      : 0 0 1px 0;
      }}
      #markdown h2 {{
        border-style      : solid;
        border-width      : 0 0 1px 0;
      }}

      #header {{
        width             : 100%;
        padding           : 10px 0;
      }}
      #header h1 ,
      #header h2 ,
      #header h3 ,
      #header h4 ,
      #header h5 ,
      #header h6 ,
      #header p {{
        padding-left      : 10px;
        padding-right     : 10px;
      }}

      #footer {{
        width             : 100%;
        text-align        : center;
        padding           : 10px 0;
      }}
      #footer h1,
      #footer h2,
      #footer h3,
      #footer h4,
      #footer h5,
      #footer h6,
      #footer p {{
        margin            : 10px;
      }}

      .center {{
        text-align        : center;
      }}

    {HtmlFormatter(style="monokai").get_style_defs('.codehilite')}
    </style>
  </head>

<body>
%header%
<div id='wrapper'>
%content%
</div>
<div style="clear:both">&nbsp;</div>
%footer%
</body>

</html>
"""

