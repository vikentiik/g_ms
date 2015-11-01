from timeit import default_timer as timer
from g_ms import logger, solve_case, parse_cases, g_quality_calc_cnt, g_find_cnt

with open('timing-sample.in') as input:
    case_cnt = 1
    cases = parse_cases(input)
    total_start = timer()
    repeat = 20
    for i in range(repeat):
        with open('log/timing-sample.out', 'a+') as output:
            output_line = 'Case #{}: {}\n'.format(case_cnt, solve_case(cases[0]))
            output.write(output_line)
            logger.info(output_line.strip())
    logger.info('total time: ' + str(timer() - total_start))
    logger.info('avg time: ' + str((timer() - total_start) / repeat))
    logger.info('quality calculations: ' + str(g_quality_calc_cnt))
    logger.info('find_all''s: ' + str(g_find_cnt))
