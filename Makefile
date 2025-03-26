# Makefile for logo scraping & grouping

.PHONY: install run clean

# Install dependencies in a virtual environment
install:
	@echo "📦 Installing Logo-Scraper dependencies..."
	@echo ""
	@echo "📌 NOTE: This will create a Python virtual environment in ./venv"
	@echo "         and install all required packages inside it."
	@echo ""
	@sudo apt update && sudo apt install -y libcairo2 libcairo2-dev
	@echo ""
	@python3 -m venv venv
	@venv/bin/pip install --upgrade pip
	@venv/bin/pip install -r requirements.txt
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "👉 To activate the virtual environment, run:"
	@echo "   source venv/bin/activate"
	@echo ""
	@echo "Then you can run the pipeline with:"
	@echo "   make run"
	@echo ""

# Run Logo Similarity script
run:
	@python3 group_logos.py

# Cleanup output files
clean:
	@echo "🧹 Cleaning output files..."
	@rm -f logo_hashes.json logo_groups.json failed_logos.txt logo_scraping_results.txt
