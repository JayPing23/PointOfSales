"""
File utility functions for Point of Sales System.
"""
import json
import csv
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox


class FileUtils:
    """Utility class for file operations and data management."""
    
    @staticmethod
    def save_to_json(data: Dict[str, Any], filename: str) -> bool:
        """
        Save data to JSON file with error handling.
        
        Args:
            data: Data to save
            filename: Target filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False
    
    @staticmethod
    def load_from_json(filename: str) -> Optional[Dict[str, Any]]:
        """
        Load data from JSON file with error handling.
        
        Args:
            filename: Source filename
            
        Returns:
            Dict or None: Loaded data or None if error
        """
        try:
            if not os.path.exists(filename):
                return {}
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading from JSON: {e}")
            return None
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str, fieldnames: List[str]) -> bool:
        """
        Export data to CSV file.
        
        Args:
            data: List of dictionaries to export
            filename: Target filename
            fieldnames: Column headers
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def get_save_filename(title: str, filetypes: List[tuple]) -> Optional[str]:
        """
        Open file dialog for saving files.
        
        Args:
            title: Dialog title
            filetypes: List of (description, extension) tuples
            
        Returns:
            str or None: Selected filename or None if cancelled
        """
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        filename = filedialog.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            defaultextension=filetypes[0][1] if filetypes else ""
        )
        root.destroy()
        return filename if filename else None
    
    @staticmethod
    def get_open_filename(title: str, filetypes: List[tuple]) -> Optional[str]:
        """
        Open file dialog for opening files.
        
        Args:
            title: Dialog title
            filetypes: List of (description, extension) tuples
            
        Returns:
            str or None: Selected filename or None if cancelled
        """
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        filename = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes
        )
        root.destroy()
        return filename if filename else None
    
    @staticmethod
    def backup_data(data: Dict[str, Any], backup_dir: str = "backups") -> bool:
        """
        Create a backup of data with timestamp.
        
        Args:
            data: Data to backup
            backup_dir: Backup directory name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = os.path.join(backup_dir, f"backup_{timestamp}.json")
            
            return FileUtils.save_to_json(data, backup_filename)
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    @staticmethod
    def validate_sale_data(sale: Dict[str, Any]) -> List[str]:
        """
        Validate sale data and return list of errors.
        
        Args:
            sale: Sale data to validate
            
        Returns:
            List[str]: List of validation errors
        """
        errors = []
        
        # Required fields
        required_fields = ['items', 'total_amount', 'timestamp']
        for field in required_fields:
            if field not in sale:
                errors.append(f"Missing required field: {field}")
        
        # Validate items
        if 'items' in sale:
            if not isinstance(sale['items'], list) or len(sale['items']) == 0:
                errors.append("Sale must have at least one item")
            else:
                for i, item in enumerate(sale['items']):
                    if not isinstance(item, dict):
                        errors.append(f"Item {i+1} must be a dictionary")
                    else:
                        if 'product_id' not in item or 'quantity' not in item:
                            errors.append(f"Item {i+1} missing product_id or quantity")
        
        # Validate total amount
        if 'total_amount' in sale:
            try:
                float(sale['total_amount'])
            except (ValueError, TypeError):
                errors.append("Total amount must be a valid number")
        
        return errors
    
    @staticmethod
    def validate_cart_item(item: Dict[str, Any]) -> List[str]:
        """
        Validate cart item data and return list of errors.
        
        Args:
            item: Cart item data to validate
            
        Returns:
            List[str]: List of validation errors
        """
        errors = []
        
        # Required fields
        required_fields = ['product_id', 'quantity']
        for field in required_fields:
            if field not in item:
                errors.append(f"Missing required field: {field}")
        
        # Validate quantity
        if 'quantity' in item:
            try:
                qty = int(item['quantity'])
                if qty <= 0:
                    errors.append("Quantity must be greater than 0")
            except (ValueError, TypeError):
                errors.append("Quantity must be a valid integer")
        
        return errors 