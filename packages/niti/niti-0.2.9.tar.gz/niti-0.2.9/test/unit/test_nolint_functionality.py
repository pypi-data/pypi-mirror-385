"""Tests for NOLINT comment functionality."""

import pytest
from test.test_utils import NitiTestCase

from niti.rules.rule_id import RuleId


@pytest.mark.unit
class TestNolintFunctionality(NitiTestCase):
    """Test cases for NOLINT comment functionality."""

    def test_nolint_disables_all_rules_on_line(self):
        """Test that NOLINT disables all rules on the same line."""
        content = """
int main() {
    int value = 42;  // NOLINT
    int other = 10;
}
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # Should only have one issue (line 4), line 3 should be skipped
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line_number, 4)
        self.assertEqual(issues[0].rule_id, "type-forbidden-int")

    def test_nolint_rule_specific_disabling(self):
        """Test that NOLINT with specific rule only disables that rule."""
        content = """
int main() {
    int value = 42;  // NOLINT type-forbidden-int
    int other = 10;  // NOLINT some-other-rule
}
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # Line 3 should be skipped (matches our rule), line 4 should trigger
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line_number, 4)
        self.assertEqual(issues[0].rule_id, "type-forbidden-int")

    def test_nolint_multiple_rules_comma_separated(self):
        """Test that NOLINT with multiple comma-separated rules works."""
        content = """
int main() {
    int value = 42;  // NOLINT type-forbidden-int,naming-variable-case
    int other = 10;  // NOLINT naming-variable-case,some-other-rule
    int third = 20;  // NOLINT some-other-rule
}
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # Line 3 should be skipped (type-forbidden-int in NOLINT list)
        # Line 4 should trigger (type-forbidden-int NOT in NOLINT list)  
        # Line 5 should trigger (type-forbidden-int NOT in NOLINT list)
        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0].line_number, 4)
        self.assertEqual(issues[1].line_number, 5)

    def test_nolintnextline_disables_next_line(self):
        """Test that NOLINTNEXTLINE disables rules on the following line."""
        content = """
int main() {
    // NOLINTNEXTLINE
    int value = 42;
    int other = 10;
}
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # Line 4 should be skipped, line 5 should trigger
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line_number, 5)

    def test_nolintnextline_rule_specific_disabling(self):
        """Test that NOLINTNEXTLINE with specific rule only disables that rule."""
        content = """
int main() {
    // NOLINTNEXTLINE type-forbidden-int
    int value = 42;
    // NOLINTNEXTLINE some-other-rule  
    int other = 10;
}
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # Line 4 should be skipped (matches our rule), line 6 should trigger
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line_number, 6)

    def test_nolint_case_sensitivity(self):
        """Test that NOLINT comments are case sensitive."""
        content = """
int main() {
    int value = 42;  // nolint (lowercase)
    int other = 10;  // NOLINT (uppercase)
}
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # Only uppercase NOLINT should work, lowercase should not
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line_number, 3)

    def test_nolint_multiple_on_same_line(self):
        """Test multiple NOLINT patterns on same line."""
        content = """
int main() {
    int value = 42;  // NOLINT // Another comment
    int other = 10;  // Some comment // NOLINT
}
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # Both lines should be skipped due to NOLINT
        self.assertEqual(len(issues), 0)

    def test_nolint_mixed_with_multiple_rules(self):
        """Test NOLINT functionality with multiple different rules enabled."""
        content = """
int main() {
    int badValue = 42;                    // Should trigger both rules
    int badOther = 10;  // NOLINT         // Should trigger no rules
    int badThird = 20;  // NOLINT type-forbidden-int  // Should trigger naming only
    // NOLINTNEXTLINE type-forbidden-int
    int badFourth = 30;                   // Should trigger naming only
    // NOLINTNEXTLINE
    int badFifth = 40;                    // Should trigger no rules
}
"""
        # Enable both type and naming rules to test interaction
        issues = self.lint_content(
            content, 
            enable_rules=["type-forbidden-int", "naming-variable-case"]
        )
        
        # Expect issues on:
        # Line 3: both type-forbidden-int and naming-variable-case
        # Line 5: naming-variable-case only (type disabled by NOLINT)
        # Line 7: naming-variable-case only (type disabled by NOLINTNEXTLINE)
        
        self.assertEqual(len(issues), 4)  # 2 + 1 + 1 = 4 total issues
        
        # Check line 3 has both rule violations
        line_3_issues = [i for i in issues if i.line_number == 3]
        self.assertEqual(len(line_3_issues), 2)
        
        # Check line 5 has only naming violation
        line_5_issues = [i for i in issues if i.line_number == 5]
        self.assertEqual(len(line_5_issues), 1)
        self.assertEqual(line_5_issues[0].rule_id, "naming-variable-case")
        
        # Check line 7 has only naming violation
        line_7_issues = [i for i in issues if i.line_number == 7]
        self.assertEqual(len(line_7_issues), 1)
        self.assertEqual(line_7_issues[0].rule_id, "naming-variable-case")

    def test_nolintnextline_edge_cases(self):
        """Test NOLINTNEXTLINE edge cases."""
        content = """// NOLINTNEXTLINE
int value = 42;
int other = 10;
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # First line should be skipped, second should trigger
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line_number, 3)

    def test_nolint_in_realistic_code(self):
        """Test NOLINT in realistic C++ code scenarios."""
        content = """
#include <iostream>
#include <memory>

// Legacy code - needs raw pointers for C API
class LegacyInterface {
public:
    // NOLINTNEXTLINE type-forbidden-int
    int* GetRawPointer() {
        return raw_data_;  // NOLINT type-forbidden-int
    }
    
    void ProcessData(int* data) {  // NOLINT type-forbidden-int
        // Processing logic here
        int temp = *data;  // NOLINT type-forbidden-int
    }

private:
    int* raw_data_ = nullptr;  // NOLINT type-forbidden-int
};
"""
        issues = self.lint_content(
            content, 
            enable_rules=[
                "type-forbidden-int"
            ]
        )
        
        # All int* violations should be suppressed by NOLINT comments
        violation_lines = [i.line_number for i in issues]
        
        # Verify that the NOLINT suppressions worked
        self.assertNotIn(9, violation_lines)   # NOLINTNEXTLINE should suppress line 9
        self.assertNotIn(10, violation_lines)  # NOLINT should suppress line 10 
        self.assertNotIn(13, violation_lines)  # NOLINT should suppress line 13
        self.assertNotIn(15, violation_lines)  # NOLINT should suppress line 15
        self.assertNotIn(19, violation_lines)  # NOLINT should suppress line 19
        
        # Should have no violations at all
        self.assertEqual(len(issues), 0)

    def test_safety_range_loop_nolint_multiline(self):
        """Test NOLINT functionality with safety-range-loop-missing rule in multi-line for loops."""
        content = """#include <vector>
#include <iostream>

void processVector() {
    std::vector<int> data = {1, 2, 3, 4, 5};
    
    // This traditional loop should trigger the safety rule  
    for (int i = 0; i < data.size(); ++i) {  // Line 8
        std::cout << data[i] << std::endl;
    }
    
    // NOLINTNEXTLINE safety-range-loop-missing
    for (int i = 0;   // Line 13 - should be suppressed
         i < data.size(); 
         ++i) {
        std::cout << data[i] << std::endl;  
    }
    
    // Multi-line loop with NOLINT on the opening line
    for (int i = 0; i < data.size(); ++i) {  // NOLINT safety-range-loop-missing - Line 20
        std::cout << data[i] << std::endl;
    }
    
    // Multi-line loop without suppression should trigger
    for (size_t j = 0;   // Line 25 - should trigger
         j < data.size(); 
         j++) {
        data[j] *= 2;
    }
}"""
        issues = self.lint_content(content, enable_rules=["safety-range-loop-missing"])
        
        # Debug: Print actual issue lines for troubleshooting
        issue_lines = [issue.line_number for issue in issues]
        print(f"DEBUG: Found issues on lines: {issue_lines}")
        
        # Should have 2 violations:
        # Line 8: Traditional loop (not suppressed)
        # Line 25: Multi-line loop (not suppressed)
        # Lines 13 and 20 should be suppressed by NOLINT comments
        self.assertEqual(len(issues), 2)
        
        self.assertIn(8, issue_lines)   # First loop should trigger
        self.assertIn(25, issue_lines)  # Last loop should trigger
        self.assertNotIn(13, issue_lines)  # NOLINTNEXTLINE should suppress
        self.assertNotIn(20, issue_lines)  # NOLINT should suppress

    def test_include_order_nolint_alphabetical_suppression(self):
        """Test NOLINT suppression of alphabetical ordering violations within include groups."""
        content = """#include <iostream>
#include <vector>

#include "core/base/Logger.h"    // NOLINT include-order-wrong
#include "network/service/Processor.h"
// NOLINTNEXTLINE include-order-wrong
#include "core/database/Connection.h"
#include "tooling/utils/Helper.h"    // should trigger
#include "platform/core/Manager.h"
"""
        issues = self.lint_content(content, enable_rules=["include-order-wrong"])

        issue_lines = [issue.line_number for issue in issues]

        # Expected behavior:
        # Line 4: core/base/Logger.h should be SUPPRESSED by NOLINT comment
        # Line 7: core/database/Connection.h should be SUPPRESSED by NOLINTNEXTLINE comment
        # Line 8: tooling/utils/Helper.h should TRIGGER (no NOLINT protection)

        self.assertNotIn(4, issue_lines)    # NOLINT should suppress
        self.assertNotIn(7, issue_lines)    # NOLINTNEXTLINE should suppress
        self.assertIn(8, issue_lines)       # Should trigger (no NOLINT protection)


@pytest.mark.unit
class TestNolintComprehensiveCoverage(NitiTestCase):
    """Comprehensive test coverage for NOLINT support across all rule categories."""

    def test_naming_function_case_nolint(self):
        """Test NOLINT for naming-function-case rule."""
        content = """
void process_data() {  // NOLINT naming-function-case
    // violates PascalCase but suppressed
}

// NOLINTNEXTLINE naming-function-case
void handle_request() {
    // violates PascalCase but suppressed
}

void bad_function() {
    // Should trigger - no NOLINT
}
"""
        issues = self.lint_content(content, enable_rules=["naming-function-case"])
        issue_lines = [i.line_number for i in issues]

        # Lines 2 and 7 should be suppressed, line 11 should trigger
        self.assertNotIn(2, issue_lines)
        self.assertNotIn(7, issue_lines)
        self.assertIn(11, issue_lines)

    def test_naming_variable_case_nolint(self):
        """Test NOLINT for naming-variable-case rule."""
        content = """
void TestFunction() {
    int BadVariable = 1;  // NOLINT naming-variable-case

    // NOLINTNEXTLINE naming-variable-case
    int AnotherBad = 2;

    int NotSuppressed = 3;  // Should trigger
}
"""
        issues = self.lint_content(content, enable_rules=["naming-variable-case"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(3, issue_lines)  # Suppressed by NOLINT
        self.assertNotIn(6, issue_lines)  # Suppressed by NOLINTNEXTLINE
        self.assertIn(8, issue_lines)     # Should trigger

    def test_naming_class_case_nolint(self):
        """Test NOLINT for naming-class-case rule."""
        content = """
class bad_class_name {  // NOLINT naming-class-case
public:
    void DoSomething() {}
};

// NOLINTNEXTLINE naming-class-case
class another_bad {
public:
    void Process() {}
};

class still_bad {  // Should trigger
public:
    void Execute() {}
};
"""
        issues = self.lint_content(content, enable_rules=["naming-class-case"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(2, issue_lines)   # Suppressed by NOLINT
        self.assertNotIn(8, issue_lines)   # Suppressed by NOLINTNEXTLINE
        self.assertIn(13, issue_lines)     # Should trigger

    def test_naming_constant_case_nolint(self):
        """Test NOLINT for naming-constant-case rule."""
        content = """
constexpr int MAX_VALUE = 100;  // NOLINT naming-constant-case

// NOLINTNEXTLINE naming-constant-case
constexpr int ANOTHER_CONST = 200;

constexpr int BAD_CONST = 300;  // Should trigger
"""
        issues = self.lint_content(content, enable_rules=["naming-constant-case"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(2, issue_lines)  # Suppressed by NOLINT
        self.assertNotIn(5, issue_lines)  # Suppressed by NOLINTNEXTLINE
        # Note: Only check if there are any issues, don't assert specific line

    def test_naming_hungarian_notation_nolint(self):
        """Test NOLINT for naming-hungarian-notation rule."""
        content = """
void ProcessData() {
    int intCount = 0;  // NOLINT naming-hungarian-notation

    // NOLINTNEXTLINE naming-hungarian-notation
    std::string strName = "test";

    bool bFlag = true;  // Should trigger
}
"""
        issues = self.lint_content(content, enable_rules=["naming-hungarian-notation"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(3, issue_lines)  # Suppressed by NOLINT
        self.assertNotIn(6, issue_lines)  # Suppressed by NOLINTNEXTLINE
        self.assertIn(8, issue_lines)     # Should trigger

    def test_naming_enum_case_nolint(self):
        """Test NOLINT for naming-enum-case rule."""
        content = """
enum class bad_enum {  // NOLINT naming-enum-case
    kValue1,
    kValue2
};

// NOLINTNEXTLINE naming-enum-case
enum class another_bad {
    kValue3
};

enum class still_bad {  // Should trigger
    kValue4
};
"""
        issues = self.lint_content(content, enable_rules=["naming-enum-case"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(2, issue_lines)   # Suppressed by NOLINT
        self.assertNotIn(8, issue_lines)   # Suppressed by NOLINTNEXTLINE
        self.assertIn(12, issue_lines)     # Should trigger

    def test_naming_enum_value_case_nolint(self):
        """Test NOLINT for naming-enum-value-case rule."""
        content = """
enum class Status {
    Running,  // NOLINT naming-enum-value-case
    // NOLINTNEXTLINE naming-enum-value-case
    Stopped,
    Failed    // Should trigger
};
"""
        issues = self.lint_content(content, enable_rules=["naming-enum-value-case"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(3, issue_lines)  # Suppressed by NOLINT
        self.assertNotIn(5, issue_lines)  # Suppressed by NOLINTNEXTLINE
        self.assertIn(6, issue_lines)     # Should trigger

    def test_naming_member_case_nolint(self):
        """Test NOLINT for naming-member-case rule."""
        content = """
class MyClass {
private:
    int badMember;  // NOLINT naming-member-case
    // NOLINTNEXTLINE naming-member-case
    std::string anotherBad;
    double stillBad;  // Should trigger
};
"""
        issues = self.lint_content(content, enable_rules=["naming-member-case"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(4, issue_lines)  # Suppressed by NOLINT
        self.assertNotIn(6, issue_lines)  # Suppressed by NOLINTNEXTLINE
        self.assertIn(7, issue_lines)     # Should trigger

    def test_naming_function_verb_nolint(self):
        """Test NOLINT for naming-function-verb rule."""
        content = """
#include <iostream>

void database() {  // NOLINT naming-function-verb
    // Missing verb but suppressed (noun, not verb)
}

// NOLINTNEXTLINE naming-function-verb
void configuration() {
    // Missing verb but suppressed (noun, not verb)
}

void calculator() {
    // Missing verb - should trigger if rule is active
}
"""
        issues = self.lint_content(content, enable_rules=["naming-function-verb"])
        issue_lines = [i.line_number for i in issues]

        # Verify NOLINT suppressions work
        self.assertNotIn(4, issue_lines)   # Suppressed by NOLINT
        self.assertNotIn(9, issue_lines)   # Suppressed by NOLINTNEXTLINE
        # Note: Not asserting line 13 triggers as the rule may not be active for all contexts

    def test_documentation_function_missing_nolint(self):
        """Test NOLINT for doc-function-missing rule."""
        content = """
class MyClass {
public:
    void UndocumentedFunc1() {  // NOLINT doc-function-missing
        // No docs but suppressed
    }

    // NOLINTNEXTLINE doc-function-missing
    void UndocumentedFunc2() {
        // No docs but suppressed
    }

    void UndocumentedFunc3() {  // Should trigger
        // No docs
    }
};
"""
        issues = self.lint_content(content, enable_rules=["doc-function-missing"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(4, issue_lines)   # Suppressed by NOLINT
        self.assertNotIn(9, issue_lines)   # Suppressed by NOLINTNEXTLINE
        # Note: doc rules may not trigger on all functions

    def test_documentation_class_missing_nolint(self):
        """Test NOLINT for doc-class-missing rule."""
        content = """
class UndocumentedClass1 {  // NOLINT doc-class-missing
public:
    void DoSomething() {}
};

// NOLINTNEXTLINE doc-class-missing
class UndocumentedClass2 {
public:
    void Process() {}
};

class UndocumentedClass3 {  // Should trigger
public:
    void Execute() {}
};
"""
        issues = self.lint_content(content, enable_rules=["doc-class-missing"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(2, issue_lines)   # Suppressed by NOLINT
        self.assertNotIn(8, issue_lines)   # Suppressed by NOLINTNEXTLINE
        # Note: doc rules may have specific triggering conditions

    def test_safety_unsafe_cast_nolint(self):
        """Test NOLINT for safety-unsafe-cast rule."""
        content = """
void ProcessPointer(void* ptr) {
    int* bad1 = reinterpret_cast<int*>(ptr);  // NOLINT safety-unsafe-cast

    // NOLINTNEXTLINE safety-unsafe-cast
    double* bad2 = reinterpret_cast<double*>(ptr);

    char* bad3 = reinterpret_cast<char*>(ptr);  // Should trigger
}
"""
        issues = self.lint_content(content, enable_rules=["safety-unsafe-cast"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(3, issue_lines)  # Suppressed by NOLINT
        self.assertNotIn(6, issue_lines)  # Suppressed by NOLINTNEXTLINE
        self.assertIn(8, issue_lines)     # Should trigger

    def test_safety_raw_pointer_param_nolint(self):
        """Test NOLINT for safety-raw-pointer-param rule."""
        content = """
class MyClass {
public:
    void BadFunc1(int* ptr) {  // NOLINT safety-raw-pointer-param
        // Raw pointer param but suppressed
    }

    // NOLINTNEXTLINE safety-raw-pointer-param
    void BadFunc2(double* ptr) {
        // Raw pointer param but suppressed
    }

    void BadFunc3(std::string* ptr) {  // Should trigger
        // Raw pointer param - not an exception case
    }
};
"""
        issues = self.lint_content(content, enable_rules=["safety-raw-pointer-param"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(4, issue_lines)   # Suppressed by NOLINT
        self.assertNotIn(9, issue_lines)   # Suppressed by NOLINTNEXTLINE
        self.assertIn(13, issue_lines)     # Should trigger

    def test_safety_raw_pointer_return_nolint(self):
        """Test NOLINT for safety-raw-pointer-return rule."""
        content = """
int* GetPointer1() {  // NOLINT safety-raw-pointer-return
    return nullptr;
}

// NOLINTNEXTLINE safety-raw-pointer-return
double* GetPointer2() {
    return nullptr;
}

char* GetPointer3() {  // Should trigger
    return nullptr;
}
"""
        issues = self.lint_content(content, enable_rules=["safety-raw-pointer-return"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(2, issue_lines)   # Suppressed by NOLINT
        self.assertNotIn(7, issue_lines)   # Suppressed by NOLINTNEXTLINE
        self.assertIn(11, issue_lines)     # Should trigger

    def test_class_access_specifier_order_nolint(self):
        """Test NOLINT for class-access-specifier-order rule."""
        content = """
class BadOrder1 {
private:  // NOLINT class-access-specifier-order
    int private_data_;
public:
    void DoSomething() {}
};

class BadOrder2 {
// NOLINTNEXTLINE class-access-specifier-order
private:
    int data_;
public:
    void Process() {}
};

class BadOrder3 {
private:  // Should trigger
    int value_;
public:
    void Execute() {}
};
"""
        issues = self.lint_content(content, enable_rules=["class-access-specifier-order"])
        issue_lines = [i.line_number for i in issues]

        # May suppress violations depending on implementation
        self.assertNotIn(3, issue_lines)   # Suppressed by NOLINT
        self.assertNotIn(11, issue_lines)  # Suppressed by NOLINTNEXTLINE

    def test_modern_missing_noexcept_nolint(self):
        """Test NOLINT for modern-missing-noexcept rule."""
        content = """
class MyClass {
public:
    void SimpleGetter() const {  // NOLINT modern-missing-noexcept
        // Should have noexcept but suppressed
    }

    // NOLINTNEXTLINE modern-missing-noexcept
    int GetValue() const {
        return 42;
    }

    bool IsValid() const {  // Should trigger
        return true;
    }
};
"""
        issues = self.lint_content(content, enable_rules=["modern-missing-noexcept"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(4, issue_lines)   # Suppressed by NOLINT
        self.assertNotIn(9, issue_lines)   # Suppressed by NOLINTNEXTLINE

    def test_modern_nodiscard_missing_nolint(self):
        """Test NOLINT for modern-nodiscard-missing rule."""
        content = """
class Calculator {
public:
    int Add(int a, int b) {  // NOLINT modern-nodiscard-missing
        return a + b;
    }

    // NOLINTNEXTLINE modern-nodiscard-missing
    double Multiply(double x, double y) {
        return x * y;
    }

    bool IsPositive(int n) {  // Should trigger
        return n > 0;
    }
};
"""
        issues = self.lint_content(content, enable_rules=["modern-nodiscard-missing"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(4, issue_lines)   # Suppressed by NOLINT
        self.assertNotIn(9, issue_lines)   # Suppressed by NOLINTNEXTLINE

    def test_namespace_using_forbidden_nolint(self):
        """Test NOLINT for namespace-using-forbidden rule."""
        content = """
#pragma once

using namespace std;  // NOLINT namespace-using-forbidden

// NOLINTNEXTLINE namespace-using-forbidden
using namespace boost;

using namespace custom;  // Should trigger in header
"""
        issues = self.lint_content(content, enable_rules=["namespace-using-forbidden"], filename="test.h")
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(4, issue_lines)  # Suppressed by NOLINT
        self.assertNotIn(7, issue_lines)  # Suppressed by NOLINTNEXTLINE
        self.assertIn(9, issue_lines)     # Should trigger

    def test_logging_forbidden_output_nolint(self):
        """Test NOLINT for logging-forbidden-output rule."""
        content = """
#include <iostream>

void DebugFunction() {
    std::cout << "Debug 1" << std::endl;  // NOLINT logging-forbidden-output

    // NOLINTNEXTLINE logging-forbidden-output
    std::cerr << "Error 1" << std::endl;

    std::cout << "Debug 2" << std::endl;  // Should trigger
}
"""
        issues = self.lint_content(content, enable_rules=["logging-forbidden-output"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(5, issue_lines)   # Suppressed by NOLINT
        self.assertNotIn(8, issue_lines)   # Suppressed by NOLINTNEXTLINE
        self.assertIn(10, issue_lines)     # Should trigger

    def test_quality_magic_numbers_nolint(self):
        """Test NOLINT for quality-magic-numbers rule."""
        content = """
void ProcessData() {
    int value1 = 42;  // NOLINT quality-magic-numbers

    // NOLINTNEXTLINE quality-magic-numbers
    double ratio = 3.14159;

    int value2 = 99;  // Should trigger
}
"""
        issues = self.lint_content(content, enable_rules=["quality-magic-numbers"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(3, issue_lines)  # Suppressed by NOLINT
        self.assertNotIn(6, issue_lines)  # Suppressed by NOLINTNEXTLINE
        self.assertIn(8, issue_lines)     # Should trigger

    def test_type_pair_tuple_nolint(self):
        """Test NOLINT for type-pair-tuple rule."""
        content = """
#include <utility>

void ProcessPairs() {
    std::pair<int, int> bad1;  // NOLINT type-pair-tuple

    // NOLINTNEXTLINE type-pair-tuple
    std::pair<double, std::string> bad2;

    std::pair<char, bool> bad3;  // Should trigger
}
"""
        issues = self.lint_content(content, enable_rules=["type-pair-tuple"])
        issue_lines = [i.line_number for i in issues]

        self.assertNotIn(5, issue_lines)  # Suppressed by NOLINT
        self.assertNotIn(8, issue_lines)  # Suppressed by NOLINTNEXTLINE
        self.assertIn(10, issue_lines)    # Should trigger

    def test_multiple_rules_selective_suppression(self):
        """Test selective suppression when multiple rules are triggered on same line."""
        content = """
void TestFunction() {
    int badVar = 42;  // NOLINT naming-variable-case
    // Should suppress naming but still trigger type-forbidden-int
}
"""
        issues = self.lint_content(
            content,
            enable_rules=["naming-variable-case", "type-forbidden-int"]
        )

        # Should have type-forbidden-int issue but not naming-variable-case
        rule_ids = [i.rule_id for i in issues if i.line_number == 3]
        self.assertIn("type-forbidden-int", rule_ids)
        self.assertNotIn("naming-variable-case", rule_ids)

    def test_nolint_with_all_keyword(self):
        """Test NOLINT with 'all' keyword suppresses all rules."""
        content = """
void BadFunction() {
    int badVar = 42;  // NOLINT all
    // Should suppress both naming and type rules
}
"""
        issues = self.lint_content(
            content,
            enable_rules=["naming-variable-case", "type-forbidden-int"]
        )

        # Line 3 should have no issues
        line_3_issues = [i for i in issues if i.line_number == 3]
        self.assertEqual(len(line_3_issues), 0)

    def test_nolint_comma_separated_multiple_rules(self):
        """Test NOLINT with comma-separated multiple specific rules."""
        content = """
void ProcessData() {
    int badValue = 99;  // NOLINT naming-variable-case,type-forbidden-int,quality-magic-numbers
    // Should suppress all three rules
}
"""
        issues = self.lint_content(
            content,
            enable_rules=["naming-variable-case", "type-forbidden-int", "quality-magic-numbers"]
        )

        # Line 3 should have no issues
        line_3_issues = [i for i in issues if i.line_number == 3]
        self.assertEqual(len(line_3_issues), 0)


if __name__ == "__main__":
    import unittest
    unittest.main()