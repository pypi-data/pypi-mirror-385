install(DIRECTORY chip DESTINATION deps
				PATTERN "chip_map_dev.json" EXCLUDE
				PATTERN "tpul_8_0" EXCLUDE)
install(DIRECTORY common DESTINATION deps)
install(DIRECTORY runtime DESTINATION deps)
install(DIRECTORY scripts DESTINATION deps)
