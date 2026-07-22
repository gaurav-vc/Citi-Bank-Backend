import uuid
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from inventory.models import Item, StockLedger

class Command(BaseCommand):
    help = 'Reconciles Item.current_stock with StockLedger transaction history.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Create missing OPENING_BALANCE entries and align ledger with current stock.',
        )

    def handle(self, *args, **options):
        fix_mode = options['fix']
        
        items = Item.objects.all().order_by('id')
        discrepancies = []
        
        self.stdout.write(self.style.MIGRATE_HEADING("Starting inventory reconciliation..."))
        
        for item in items:
            # Get all ledger entries for this item
            ledgers = StockLedger.objects.filter(item=item).order_by('timestamp')
            
            # Calculate stock from ledgers
            ledger_stock = 0
            has_opening = False
            earliest_timestamp = None
            
            for ledger in ledgers:
                if earliest_timestamp is None:
                    earliest_timestamp = ledger.timestamp
                
                t_type = ledger.transaction_type
                qty = ledger.quantity
                
                if t_type in ['OPENING_BALANCE', 'GRN_RECEIPT', 'MANUAL_ADJUSTMENT', 'RETURN_FROM_SITE']:
                    ledger_stock += qty
                    if t_type == 'OPENING_BALANCE':
                        has_opening = True
                elif t_type == 'GOODS_ISSUE':
                    ledger_stock -= qty
                elif t_type == 'RETURN_TO_VENDOR':
                    # If stock actually changed, account for it
                    if ledger.stock_after != ledger.stock_before:
                        ledger_stock += (ledger.stock_after - ledger.stock_before)
                        
            current_stock = item.current_stock
            difference = current_stock - ledger_stock
            
            recommendation = "No action required."
            if difference != 0:
                if difference > 0:
                    recommendation = f"Create OPENING_BALANCE of {difference} unit(s) to reconcile ledger."
                else:
                    recommendation = f"Discrepancy of {difference} unit(s). Adjust ledger to align with current stock."
            
            discrepancies.append({
                'item': item,
                'current_stock': current_stock,
                'ledger_stock': ledger_stock,
                'difference': difference,
                'has_opening': has_opening,
                'earliest_timestamp': earliest_timestamp,
                'recommendation': recommendation
            })
            
        # Display report
        self.stdout.write("\n" + "="*80)
        self.stdout.write(f"{'Item ID':<10} | {'Item Name':<30} | {'Current':<8} | {'Ledger':<8} | {'Diff':<6} | {'Recommendation'}")
        self.stdout.write("="*80)
        
        discrepant_count = 0
        for d in discrepancies:
            item = d['item']
            diff = d['difference']
            if diff != 0:
                discrepant_count += 1
                style_func = self.style.WARNING
            else:
                style_func = self.style.SUCCESS
                
            self.stdout.write(style_func(
                f"{item.id:<10} | {item.name[:30]:<30} | {d['current_stock']:<8} | {d['ledger_stock']:<8} | {diff:<6} | {d['recommendation']}"
            ))
            
        self.stdout.write("="*80)
        self.stdout.write(f"Total items: {len(discrepancies)} | Discrepant items: {discrepant_count}\n")
        
        if not fix_mode:
            self.stdout.write(self.style.SUCCESS("Reconciliation check completed in read-only mode."))
            return
            
        if discrepant_count == 0:
            self.stdout.write(self.style.SUCCESS("All items are fully reconciled. No changes to apply."))
            return
            
        # Fix Mode logic
        self.stdout.write(self.style.WARNING("FIX MODE ACTIVATED: The command will create missing OPENING_BALANCE entries to align the ledger."))
        self.stdout.write("Are you sure you want to proceed with these changes? (yes/no): ")
        
        # In django management commands, input() is standard
        response = input().strip().lower()
        if response not in ['yes', 'y']:
            self.stdout.write(self.style.ERROR("Reconciliation cancelled by user."))
            return
            
        fixed_count = 0
        with transaction.atomic():
            for d in discrepancies:
                if d['difference'] == 0:
                    continue
                
                item = d['item']
                diff = d['difference']
                earliest_ts = d['earliest_timestamp']
                
                # We need to create an opening balance entry
                # Let's say opening balance should have happened before any other entries
                if earliest_ts:
                    target_ts = earliest_ts - timedelta(seconds=60)
                else:
                    target_ts = timezone.now() - timedelta(days=30)
                
                # Determine stock before and stock after for the opening balance
                # Stock before opening balance is always 0
                stock_before = 0
                stock_after = diff
                
                ledger_id = f"SL-{uuid.uuid4().hex[:8].upper()}"
                
                # Create the StockLedger entry
                ledger_entry = StockLedger.objects.create(
                    id=ledger_id,
                    transaction_type='OPENING_BALANCE',
                    source_type='SYSTEM',
                    source_id='OPENING-STOCK',
                    item=item,
                    quantity=diff,
                    stock_before=stock_before,
                    stock_after=stock_after,
                    remarks='System-generated opening balance for reconciliation.',
                    reason='Reconciliation'
                )
                
                # Update the timestamp using update() to bypass auto_now_add
                StockLedger.objects.filter(id=ledger_entry.id).update(timestamp=target_ts)
                
                # Now, if other transactions exist, we should adjust their stock_before and stock_after
                # so that the running balance is chronologically correct!
                # Let's update all subsequent transactions for this item
                current_running_stock = stock_after
                subsequent_ledgers = StockLedger.objects.filter(item=item).exclude(id=ledger_entry.id).order_by('timestamp')
                
                for sub_ledger in subsequent_ledgers:
                    sub_qty = sub_ledger.quantity
                    sub_type = sub_ledger.transaction_type
                    
                    sub_before = current_running_stock
                    if sub_type in ['OPENING_BALANCE', 'GRN_RECEIPT', 'MANUAL_ADJUSTMENT', 'RETURN_FROM_SITE']:
                        sub_after = sub_before + sub_qty
                    elif sub_type == 'GOODS_ISSUE':
                        sub_after = sub_before - sub_qty
                    elif sub_type == 'RETURN_TO_VENDOR':
                        if sub_ledger.stock_after != sub_ledger.stock_before:
                            sub_after = sub_before + (sub_ledger.stock_after - sub_ledger.stock_before)
                        else:
                            sub_after = sub_before
                    else:
                        sub_after = sub_before
                        
                    # Update this sub_ledger
                    StockLedger.objects.filter(id=sub_ledger.id).update(
                        stock_before=sub_before,
                        stock_after=sub_after
                    )
                    current_running_stock = sub_after
                
                fixed_count += 1
                self.stdout.write(self.style.SUCCESS(f"Aligned ledger for item {item.id} ({item.name}) with OPENING_BALANCE of {diff}."))
                
        self.stdout.write(self.style.SUCCESS(f"Reconciliation fix completed. Successfully aligned {fixed_count} item(s)."))
