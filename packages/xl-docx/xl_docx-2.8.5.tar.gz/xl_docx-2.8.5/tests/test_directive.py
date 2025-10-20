from xl_docx.compiler.processors.directive import DirectiveProcessor
from xl_docx.compiler import XMLCompiler

class TestDirectiveProcessor:
    """测试DirectiveProcessor类的功能"""
    
    def test_process_v_if_simple(self):
        """测试处理简单的if指令"""
        xml = '<div if="condition">content</div>'
        result = DirectiveProcessor._process_v_if(xml)
        expected = '($ if condition $)<div>content</div>($ endif $)'
        assert result == expected
        xml = '<div if="condition"><div>content</div></div>'
        result = DirectiveProcessor._process_v_if(xml)
        expected = '($ if condition $)<div><div>content</div></div>($ endif $)'
        assert result == expected
    
    def test_process_v_if_with_attributes(self):
        """测试处理带属性的if指令"""
        xml = '<div class="test" if="condition" id="main">content</div>'
        result = DirectiveProcessor._process_v_if(xml)
        expected = '($ if condition $)<div class="test" id="main">content</div>($ endif $)'
        assert result == expected
    
    def test_process_v_if_multiple_attributes(self):
        """测试处理多个属性的if指令"""
        xml = '<span if="show" class="highlight" style="color: red">text</span>'
        result = DirectiveProcessor._process_v_if(xml)
        expected = '($ if show $)<span class="highlight" style="color: red">text</span>($ endif $)'
        assert result == expected
    
    def test_process_v_if_no_matching_tags(self):
        """测试没有if指令的情况"""
        xml = '<div>content</div>'
        result = DirectiveProcessor._process_v_if(xml)
        assert result == xml
    
    def test_process_v_if_multiple_elements(self):
        """测试处理多个if元素"""
        xml = '''
        <div if="condition1">content1</div>
        <span if="condition2">content2</span>
        '''
        result = DirectiveProcessor._process_v_if(xml)
        assert '($ if condition1 $)' in result
        assert '($ if condition2 $)' in result
        assert '($ endif $)' in result
    
    def test_process_v_for_simple(self):
        """测试处理简单的for指令"""
        xml = '<div for="item in items">content</div>'
        result = DirectiveProcessor._process_v_for(xml)
        expected = '($ for item in items $)<div>content</div>($ endfor $)'
        assert result == expected
    
    def test_process_v_for_with_attributes(self):
        """测试处理带属性的for指令"""
        xml = '<li for="item in list" class="item">content</li>'
        result = DirectiveProcessor._process_v_for(xml)
        expected = '($ for item in list $)<li class="item">content</li>($ endfor $)'
        assert result == expected
    
    def test_process_v_for_complex_expression(self):
        """测试处理复杂的for表达式"""
        xml = '<div for="(item, index) in items">content</div>'
        result = DirectiveProcessor._process_v_for(xml)
        expected = '($ for (item, index) in items $)<div>content</div>($ endfor $)'
        assert result == expected
    
    def test_process_v_for_no_matching_tags(self):
        """测试没有for指令的情况"""
        xml = '<div>content</div>'
        result = DirectiveProcessor._process_v_for(xml)
        assert result == xml
    
    def test_process_v_for_multiple_elements(self):
        """测试处理多个for元素"""
        xml = '''
        <div for="item in items">content1</div>
        <span for="element in elements">content2</span>
        '''
        result = DirectiveProcessor._process_v_for(xml)
        assert '($ for item in items $)' in result
        assert '($ for element in elements $)' in result
        assert '($ endfor $)' in result
    
    def test_compile_full_process(self):
        """测试完整的编译过程"""
        xml = '''
        <div if="show">conditional content</div>
        <span for="item in items">item content</span>
        '''
        result = DirectiveProcessor.compile(xml)
        assert '($ if show $)' in result
        assert '($ for item in items $)' in result
        assert '($ endif $)' in result
        assert '($ endfor $)' in result
    
    def test_compile_no_directives(self):
        """测试没有指令的编译"""
        xml = '<div>content</div>'
        result = DirectiveProcessor.compile(xml)
        assert result == xml
    
    def test_compile_mixed_content(self):
        """测试混合内容的编译"""
        xml = '''
        <div>normal content</div>
        <div if="condition">conditional content</div>
        <span>more content</span>
        <li for="item in list">list item</li>
        '''
        result = DirectiveProcessor.compile(xml)
        assert 'normal content' in result
        assert '($ if condition $)' in result
        assert 'more content' in result
        assert '($ for item in list $)' in result
    
    def test_decompile_v_if_simple(self):
        """测试反编译简单的if指令"""
        xml = '($ if condition $)<div>content</div>($ endif $)'
        result = DirectiveProcessor._decompile_v_if(xml)
        expected = '<div if="condition">content</div>'
        assert result == expected
    
    def test_decompile_v_if_with_attributes(self):
        """测试反编译带属性的if指令"""
        xml = '($ if show $)<div class="test" id="main">content</div>($ endif $)'
        result = DirectiveProcessor._decompile_v_if(xml)
        expected = '<div if="show" class="test" id="main">content</div>'
        assert result == expected
    
    def test_decompile_v_for_simple(self):
        """测试反编译简单的for指令"""
        xml = '($ for item in items $)<div>content</div>($ endfor $)'
        result = DirectiveProcessor._decompile_v_for(xml)
        expected = '<div for="item in items">content</div>'
        assert result == expected
    
    def test_decompile_v_for_with_attributes(self):
        """测试反编译带属性的for指令"""
        xml = '($ for item in list $)<li class="item">content</li>($ endfor $)'
        result = DirectiveProcessor._decompile_v_for(xml)
        expected = '<li for="item in list" class="item">content</li>'
        assert result == expected
    
    def test_decompile_v_for_complex_expression(self):
        """测试反编译复杂的for表达式"""
        xml = '($ for (item, index) in items $)<div>content</div>($ endfor $)'
        result = DirectiveProcessor._decompile_v_for(xml)
        expected = '<div for="(item, index) in items">content</div>'
        assert result == expected
    
    def test_decompile_full_process(self):
        """测试完整的反编译过程"""
        xml = '''
        ($ if show $)<div>conditional content</div>($ endif $)
        ($ for item in items $)<span>item content</span>($ endfor $)
        '''
        result = DirectiveProcessor.decompile(xml)
        assert 'if="show"' in result
        assert 'for="item in items"' in result
    
    def test_decompile_no_jinja_tags(self):
        """测试没有Jinja2标签的反编译"""
        xml = '<div>content</div>'
        result = DirectiveProcessor.decompile(xml)
        assert result == xml
    
    def test_decompile_mixed_content(self):
        """测试混合内容的反编译"""
        xml = '''
        <div>normal content</div>
        ($ if condition $)<div>conditional content</div>($ endif $)
        <span>more content</span>
        ($ for item in list $)<li>list item</li>($ endfor $)
        '''
        result = DirectiveProcessor.decompile(xml)
        assert 'normal content' in result
        assert 'if="condition"' in result
        assert 'more content' in result
        assert 'for="item in list"' in result
    
    def test_process_v_if_missing_closing_tag(self):
        """测试if指令缺少结束标签的情况"""
        xml = '<div if="condition">content'
        result = DirectiveProcessor._process_v_if(xml)
        # 应该返回原始内容，因为没有找到结束标签
        assert result == xml
    
    def test_process_v_for_missing_closing_tag(self):
        """测试for指令缺少结束标签的情况"""
        xml = '<div for="item in items">content'
        result = DirectiveProcessor._process_v_for(xml)
        # 应该返回原始内容，因为没有找到结束标签
        assert result == xml
    
    def test_process_v_if_nested_content(self):
        """测试if指令包含嵌套内容"""
        xml = '<div if="condition"><span>nested</span>content</div>'
        result = DirectiveProcessor._process_v_if(xml)
        expected = '($ if condition $)<div><span>nested</span>content</div>($ endif $)'
        assert result == expected
    
    def test_process_v_for_nested_content(self):
        """测试for指令包含嵌套内容"""
        xml = '<div for="item in items"><span>nested</span>content</div>'
        result = DirectiveProcessor._process_v_for(xml)
        expected = '($ for item in items $)<div><span>nested</span>content</div>($ endfor $)'
        assert result == expected
    
    def test_process_v_if_complex_condition(self):
        """测试if指令包含复杂条件"""
        xml = '<div if="user.isAdmin && showContent">content</div>'
        result = DirectiveProcessor._process_v_if(xml)
        expected = '($ if user.isAdmin && showContent $)<div>content</div>($ endif $)'
        assert result == expected
    
    def test_process_v_for_complex_loop(self):
        """测试for指令包含复杂循环"""
        xml = '<div for="item in filteredItems">content</div>'
        result = DirectiveProcessor._process_v_for(xml)
        expected = '($ for item in filteredItems $)<div>content</div>($ endfor $)'
        assert result == expected 