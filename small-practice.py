from g_ms import logger, solve_case, parse_cases

with open('A-small-practice.in') as input:
    case_cnt = 1
    for case in parse_cases(input):
        with open('log/A-small-practice.out', 'a+') as output:
            output_line = 'Case #{}: {}\n'.format(case_cnt, solve_case(case))
            output.write(output_line)
            logger.info(output_line.strip())
            case_cnt += 1

