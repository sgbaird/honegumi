# # NOTE: In addition to testing for whether errors are raised, the following was
# # also a way to capture output and possibly display that directly to the user in
# # the honegumi script (or append to the colab notebook). However, with the move
# # to hypothesis testing given the large computational burden of exhausting
# # testing, I think it makes sense to shelf this.

# if not hg.skip_tests:
#     print("Running tests...")

#     # run pytest on all or just one of the test scripts
#     collector = ResultsCollector()
#     file_filter = (
#         core_cst.TEST_TEMPLATE_DIR if not hg.dummy else first_test_template_path
#     )
#     # file_filter = TEST_TEMPLATE_DIR
#     retcode = pytest.main(["-v", file_filter], plugins=[collector])

#     for report in collector.reports:
#         print("id:", report.nodeid, "outcome:", report.outcome)  # etc

#     print("exit code:", collector.exitcode)
#     print(
#         "passed:",
#         collector.num_passed,
#         "failed:",
#         collector.num_failed,
#         "xfailed:",
#         collector.num_xfailed,
#         "skipped:",
#         collector.num_skipped,
#     )
#     print("total duration:", collector.total_duration)

#     report_data = []

#     for report in collector.reports:
#         # grab the needed info from the report
#         report_info = {
#             "stderr": report.capstderr,
#             "stdout": report.capstdout,
#             "caplog": report.caplog,
#             "passed": report.passed,
#             "duration": report.duration,
#             "nodeid": report.nodeid,
#             "fspath": report.fspath,
#         }

#         # extract the stem and remove the `_test` prefix
#         stem = Path(report.fspath).stem
#         assert stem.startswith("test_"), f"stem {stem} does not start with `test_`"
#         stem = stem[5:]

#         # unpack the stem into a dictionary
#         unpacked_stem = unpack_rendered_template_stem(stem)
#         report_datum = {**unpacked_stem, **report_info}
#         report_data.append(report_datum)

#     report_df = pd.DataFrame(report_data)
# else:
#     report_df = None

# # concatenate the two dataframes to merge the columns based on option_names
# # (i.e., the keys)
# if report_df is not None:
#     merged_df = pd.merge(data_df, report_df, on=hg.option_names, how="outer")
# else:
#     merged_df = data_df.copy()
#     merged_df["passed"] = True

# # find the configs that either failed or were incompatible

# invalid_configs = merged_df[
#     (merged_df["passed"] == False)
#     | (merged_df[core_cst.IS_COMPATIBLE_KEY] == False)  # noqa
# ][hg.option_names].to_dict(orient="records")

# # extract the values for each option name
# invalid_configs = [
#     [str(opt[option_name]) for option_name in hg.visible_option_names]
#     for opt in invalid_configs
# ]
