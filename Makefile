# Makefile for logo scraping & grouping

.PHONY: run clean

# Run Logo Similarity script
run:
	@python group_logos.py

# Cleanup output files
clean:
	@echo "🧹 Cleaning output files..."
	@rm -f logo_hashes.json logo_groups.json failed_logos.txt logo_scraping_results.txt
