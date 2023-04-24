#very_dense_boi
__import__("onedenseboi")
__import__("os");

base64=__import__("base64");
np=__import__("numpy");
sys=__import__("sys");
textwrap=__import__("textwrap");

ws_b64='XHUwMDIw';
ws_b64_bytes=ws_b64.encode('ascii');
ws_bytes=base64.b64decode(ws_b64_bytes);
raw_ws=ws_bytes.decode('ascii');
ws=bytes(raw_ws,'utf-8').decode('unicode_escape');

us='_';
filepath=__import__('__main__').__file__;
endchars={':',';',',','\\'};
imports={'from','import'};
quotedsemicolon="';'";
newline='\n';

quotes1='\'\'\'';
quotes2='"""';
commentenabled=0;
"""
exec-part;
"""
exec("""def_getmsg(idx,line,linelength):
____return_f\'\'\'__File_\"{filepath}\",_line_{idx_+_1}\n____{line}\n{\'\':>{linelength+4}}^\nSyntaxError:_expected_{quotedsemicolon}\'\'\';""".replace(us,ws));

exec(f'''def_createerrmsg(idx,line):
____linelength=len(line);
____errmsg=getmsg(idx,line,linelength);
____errmsg=textwrap.dedent(errmsg).lstrip({newline});
____print(errmsg,file=sys.stderr);
____sys.exit(1)'''.replace(us,ws));

exec("""with_open(filepath,'r')_as_f:
____lines=f.readlines()""".replace(us,ws));

exec("""for_idx,line_in_enumerate(lines):
____line=line.strip();
____isswitcher=int(line.startswith(quotes1)_or_line.startswith(quotes2));
____commentenabled=(isswitcher+commentenabled)%2;
____isvalid=int(not(line)_or_any(line.startswith(x)_for_x_in_imports)_or_any(line.endswith(x)_for_x_in_endchars)_or_line[0]=='#');
____exec('#'*(commentenabled+isvalid+isswitcher)+'createerrmsg(idx,line)');
""".replace(us,ws));

print('Semicolon_vibe_check_passed.'.replace(us,ws));

