from xl_docx.compiler.processors.base import BaseProcessor
from xl_docx.compiler.processors.paragraph.image import ImageProcessor
import re
from jinja2 import Template


class ParagraphProcessor(BaseProcessor):
    """处理段落相关的XML标签"""
    
    # 正则表达式模式常量，提高可读性
    XL_P_PARAGRAPH_PATTERN = r'''
        <xl-p                        # 开始标签
        (?:[^>]*style="([^"]+)")?   # 可选的style属性
        [^>]*>                      # 其他属性
        (.*?)                       # 内容（非贪婪匹配）
        </xl-p>                     # 结束标签
    '''
    
    XL_SPAN_PATTERN = r'''
        <xl-span                     # 开始标签
        (?:[^>]*style="([^"]+)")?   # 可选的style属性
        [^>]*>                      # 其他属性
        (.*?)                       # 内容（非贪婪匹配）
        </xl-span>                  # 结束标签
    '''
    
    XL_SIGNATURE_PATTERN = r'''
        <xl-signature\s+             # 开始标签
        data="([^"]+)"\s+           # data属性
        height="([^"]+)"\s*         # height属性
        ></xl-signature>            # 结束标签
    '''
    
    XL_BLOCK_PATTERN = r'''
        <xl-block\s+                # 开始标签
        text="([^"]*)"              # text属性
        (?:\s+style="([^"]+)")?     # 可选的style属性
        [^>]*>                      # 其他属性
        (?:.*?</xl-block>)?         # 可选的结束标签
    '''
    
    # Word文档相关模式
    W_P_PARAGRAPH_PATTERN = r'<w:p[^>]*?>(.*?)</w:p>'
    W_P_EMPTY_PATTERN = r'<w:p(?![a-zA-Z])([^>]*?)/>'
    W_R_RUN_PATTERN = r'<w:r(?:\s+[^>]*)?>(.*?)</w:r>'
    W_T_TEXT_PATTERN = r'<w:t(?:\s+[^>]*)?>(.*?)</w:t>'
    
    # Word文档属性模式
    W_JC_ALIGN_PATTERN = r'<w:jc\s+w:val="([^"]+)"/>'
    W_SPACING_PATTERN = r'<w:spacing\s+([^/>]+)/>'
    W_BEFORE_SPACING_PATTERN = r'w:before="([^"]+)"'
    W_AFTER_SPACING_PATTERN = r'w:after="([^"]+)"'
    W_RFONTS_PATTERN = r'<w:rFonts\s+w:ascii="([^"]+)"[^/]+w:cs="([^"]+)"'
    W_SZ_SIZE_PATTERN = r'<w:sz\s+w:val="([^"]+)"/>'
    W_U_UNDERLINE_PATTERN = r'<w:u w:val="([^>]*)"/>'
    
    @classmethod
    def compile(cls, xml: str) -> str:
        """将xl-p标签转换为w:p标签"""
        def process_paragraph(match):
            style_str = match.group(1) or ''
            content = match.group(2).strip()
            styles = cls._parse_style_str(style_str)

            # 构建段落属性
            p_props_str = '<w:pPr>'
            align, margin_top, margin_bottom, margin_left, margin_right, line_height, english, chinese, font_size, font_weight, spacing = cls.retrieve(styles, \
                ['align', 'margin-top', 'margin-bottom', 'margin-left', 'margin-right', 'line-height', 'english', 'chinese', 'font-size', 'font-weight', 'spacing'])
            
            # 添加对齐方式
            p_props_str += f'<w:jc w:val="{align}"/>' if align else ''
            
            # 添加缩进设置
            ind_attrs = []
            if margin_left:
                ind_attrs.append(f'w:start="{margin_left}"')
            if margin_right:
                ind_attrs.append(f'w:end="{margin_right}"')
            if ind_attrs:
                p_props_str += f'<w:ind {" ".join(ind_attrs)}/>'
            
            # 添加间距设置
            spacing_attr_str = ''
            spacing_attr_str += f'w:before="{margin_top}" ' if margin_top else ''
            spacing_attr_str += f'w:after="{margin_bottom}"' if margin_bottom else ''
            spacing_attr_str += f'w:line="{line_height}" ' if line_height else ''
            spacing_attr_str += f'w:val="{spacing}" ' if spacing else ''
            p_props_str += f'<w:spacing {spacing_attr_str}/>' if spacing_attr_str else ''
            p_props_str += '</w:pPr>'
            
            # 构建运行属性
            r_props_str = '<w:rPr>'
            # 添加字体设置
            r_props_str += f'<w:rFonts w:ascii="{english}" w:cs="{chinese}" w:eastAsia="{english}" w:hAnsi="{english}" w:hint="eastAsia"/>' if (english and chinese) else ''
            r_props_str += f'<w:kern w:val="0"/>' if font_size else ''
            r_props_str += f'<w:sz w:val="{font_size}"/>' if font_size else ''
            r_props_str += f'<w:szCs w:val="{font_size}"/>' if font_size else ''
            r_props_str += f'<w:b/>' if font_weight == 'bold' else ''
            # 添加颜色设置
            color = cls.retrieve(styles, ['color'])[0]
            r_props_str += f'<w:color w:val="{color}"/>' if color else ''
            r_props_str += '</w:rPr>'

     
            def process_span(match):
                style_str = match.group(1) or ''
                content = match.group(2).strip()
                styles = cls._parse_style_str(style_str)
                underline, font_size, font_weight, color, spacing = cls.retrieve(styles, ['underline', 'font-size', 'font-weight', 'color', 'spacing'])
                r_props_str_ = r_props_str
                r_props_str_inner = f'<w:u w:val="{underline}"/>' if underline else ''
                r_props_str_inner += f'<w:sz w:val="{font_size}"/>' if font_size else ''
                r_props_str_inner += f'<w:b/>' if font_weight == 'bold' else ''
                r_props_str_inner += f'<w:color w:val="{color}"/>' if color else ''
                r_props_str_inner += f'<w:spacing w:val="{spacing}"/>' if spacing else ''
                r_props_str_inner += '</w:rPr>'
                r_props_str_inner = r_props_str_.replace('</w:rPr>', r_props_str_inner)

                # 检查内容是否包含已编译的图片标签
                if '<w:r>' in content and '<w:pict>' in content:
                    # 如果包含图片，需要将span的样式应用到图片的w:r标签上
                    # 找到所有的w:r标签并添加样式
                    import re
                    def add_style_to_run(match):
                        run_content = match.group(0)
                        # 在w:r标签内添加r_props_str_inner
                        if '<w:rPr>' in run_content:
                            # 如果已经有rPr，替换它
                            run_content = re.sub(r'<w:rPr>.*?</w:rPr>', r_props_str_inner, run_content, flags=re.DOTALL)
                        else:
                            # 如果没有rPr，在w:r开始后添加
                            run_content = run_content.replace('<w:r>', f'<w:r>{r_props_str_inner}')
                        return run_content
                    
                    # 处理所有的w:r标签
                    content = re.sub(r'<w:r[^>]*>.*?</w:r>', add_style_to_run, content, flags=re.DOTALL)
                    return content
                else:
                    # 普通文本内容，包装在w:t中
                    return f'<w:r>{r_props_str_inner}<w:t xml:space="preserve">{content}</w:t></w:r>'
            
            # 如果内容中没有出现<，直接包裹为<xl-span>
            if '<' not in content:
                content = f'<xl-span>{content}</xl-span>'
            content = cls._process_tag(content, cls.XL_SPAN_PATTERN, process_span)
            data = f'<w:p>{p_props_str}{content}</w:p>'
            return data
        
        # 先处理 xl-block 标签
        xml = cls.process_block(xml)
        # 处理图片标签
        xml = ImageProcessor().compile(xml)
        # 再处理普通的 xl-p 标签
        data = cls._process_tag(xml, cls.XL_P_PARAGRAPH_PATTERN, process_paragraph)
        return data
    
    @classmethod
    def process_block(cls, xml: str) -> str:
        """处理 xl-block 标签，将其转换为 Jinja2 模板代码"""
        def process_block_match(match):
            text_content = match.group(1) or ''
            style_str = match.group(2) or ''
            
            if not text_content:
                return ''
            
            # 生成 Jinja2 模板代码
            jinja_template = f'''($ with $)
($ set paragraphs={text_content}.split('\\n') $)
($ for paragraph in paragraphs $)
<xl-p{f' style="{style_str}"' if style_str else ''}>
    <xl-span>((paragraph))</xl-span>
</xl-p>
($ endfor $)
($ endwith $)'''
            return jinja_template
        
        return cls._process_tag(xml, cls.XL_BLOCK_PATTERN, process_block_match)
    

    @classmethod
    def decompile(cls, xml: str) -> str:
        """将Ww:p标签转换为xl-p标签"""
        def process_word_paragraph(match):
            full_p = match.group(0)
            content = match.group(1)
            
            # 提取样式属性
            styles = {}
            
            # 提取对齐方式
            align_match = re.search(r'<w:jc\s+w:val="([^"]+)"/>', content)
            if align_match:
                styles['align'] = align_match.group(1)
            
            # 提取间距
            spacing_match = re.search(r'<w:spacing\s+([^/>]+)/>', content)
            if spacing_match:
                spacing_attrs = spacing_match.group(1)
                before_match = re.search(r'w:before="([^"]+)"', spacing_attrs)
                after_match = re.search(r'w:after="([^"]+)"', spacing_attrs)
                line_match = re.search(r'w:line="([^"]+)"', spacing_attrs)
                if before_match:
                    styles['margin-top'] = before_match.group(1)
                if after_match:
                    styles['margin-bottom'] = after_match.group(1)
                if line_match:
                    styles['line-height'] = line_match.group(1)
            
            # 提取缩进
            ind_match = re.search(r'<w:ind\s+([^/>]+)/>', content)
            if ind_match:
                ind_attrs = ind_match.group(1)
                start_match = re.search(r'w:start="([^"]+)"', ind_attrs)
                end_match = re.search(r'w:end="([^"]+)"', ind_attrs)
                if start_match:
                    styles['margin-left'] = start_match.group(1)
                if end_match:
                    styles['margin-right'] = end_match.group(1)
            
            # 提取字体信息
            font_match = re.search(r'<w:rFonts\s+w:ascii="([^"]+)"[^/]+w:cs="([^"]+)"', content)
            if font_match:
                styles['english'] = font_match.group(1)
                styles['chinese'] = font_match.group(2)
            
            # 提取字体大小
            size_match = re.search(r'<w:sz\s+w:val="([^"]+)"/>', content)
            if size_match:
                styles['font-size'] = size_match.group(1)
            
            # 检查是否加粗
            if '<w:b/>' in content:
                styles['font-weight'] = 'bold'
            
            # 提取颜色信息
            color_match = re.search(r'<w:color\s+w:val="([^"]+)"/>', content)
            if color_match:
                styles['color'] = color_match.group(1)

            def process_r(match):
                content = match.group(1).strip()
                r_styles = {}
                underline_match = re.search(r'<w:u w:val="([^>]*)"/>', content)
                if underline_match:
                    underline = underline_match.group(1)
                    r_styles['underline'] = underline
                # 提取颜色信息
                color_match = re.search(r'<w:color\s+w:val="([^"]+)"/>', content)
                if color_match:
                    r_styles['color'] = color_match.group(1)
                # 提取spacing信息
                spacing_match = re.search(r'<w:spacing\s+w:val="([^"]+)"/>', content)
                if spacing_match:
                    r_styles['spacing'] = spacing_match.group(1)
                r_style_str = cls._build_style_str(r_styles)

                def process_t(match):
                    content = match.group(1)
                    return f'{content}'
                
                # 处理文本内容
                matches = list(re.finditer(cls.W_T_TEXT_PATTERN, content, re.DOTALL))
                content = ''
                for match in matches:
                    full_r = match.group(0)
                    full_r = cls._process_tag(full_r, cls.W_T_TEXT_PATTERN, process_t)
                    content += full_r
                
                # 只有当样式不为空时才添加style属性
                style_attr = f' style="{r_style_str}"' if r_style_str else ""
                return f'<xl-span{style_attr}>{content}</xl-span>'
            
            # 处理运行标签
            matches = list(re.finditer(cls.W_R_RUN_PATTERN, content, re.DOTALL))
            content = ''
            for match in matches:
                full_t = match.group(0)
                full_t = cls._process_tag(full_t, cls.W_R_RUN_PATTERN, process_r)
                content += full_t
            
            # 合并相邻的xl-span标签
            content = cls._merge_adjacent_spans(content)
            
            # 构建样式字符串
            style_str = cls._build_style_str(styles)
            style_attr = f' style="{style_str}"' if style_str else ""
            
            # 如果没有内容但有样式，返回带样式的空段落
            if not content and style_str:
                return f'<xl-p{style_attr}></xl-p>'
            
            return f'<xl-p{style_attr}>{content}</xl-p>'
        
        # 处理空段落标签
        xml = re.sub(cls.W_P_EMPTY_PATTERN, r'<w:p\1></w:p>', xml)
        return cls._process_tag(xml, cls.W_P_PARAGRAPH_PATTERN, process_word_paragraph)

    @classmethod
    def _merge_adjacent_spans(cls, content: str) -> str:
        """合并相邻的xl-span标签，当它们的样式相同或都不存在样式时"""
        # 使用正则表达式匹配xl-span标签
        span_pattern = r'<xl-span(?:\s+style="([^"]+)")?[^>]*>(.*?)</xl-span>'
        
        # 找到所有的span标签
        spans = []
        pos = 0
        while pos < len(content):
            match = re.search(span_pattern, content[pos:], re.DOTALL)
            if not match:
                break
            
            style = match.group(1) or ""
            span_content = match.group(2)
            spans.append((style, span_content, pos + match.start(), pos + match.end()))
            pos += match.end()
        
        if len(spans) <= 1:
            return content
        
        # 合并相邻的相同样式的span
        merged_spans = []
        i = 0
        while i < len(spans):
            current_style, current_content, start_pos, end_pos = spans[i]
            merged_content = current_content
            
            # 查找后续的相同样式的span
            j = i + 1
            while j < len(spans):
                next_style, next_content, next_start, next_end = spans[j]
                if next_style == current_style:
                    merged_content += next_content
                    end_pos = next_end
                    j += 1
                else:
                    break
            
            merged_spans.append((current_style, merged_content, start_pos, end_pos))
            i = j
        
        # 重建内容
        result = ""
        last_end = 0
        
        for style, span_content, start_pos, end_pos in merged_spans:
            # 添加span之间的文本
            result += content[last_end:start_pos]
            
            # 添加合并后的span
            style_attr = f' style="{style}"' if style else ""
            result += f'<xl-span{style_attr}>{span_content}</xl-span>'
            
            last_end = end_pos
        
        # 添加剩余的文本
        result += content[last_end:]
        
        return result
