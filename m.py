import time
from telethon.sync import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError,
    FloodWaitError,
    ChannelPrivateError,
    UsernameNotOccupiedError,
    PeerFloodError,
    UserPrivacyRestrictedError
)

def print_banner():
    print("\n\033[1;36m" + "="*50)
    print(" TELEGRAM MEMBER FORWARDING TOOL ")
    print("="*50 + "\033[0m")
    print("\033[1;33mNote: Use responsibly to avoid account restrictions\033[0m\n")

def main():
    print_banner()
    
    # API credentials (replace with yours)
    API_ID = 24181054
    API_HASH = 'f026732daa0b906a8de4fe487c614ee0'
    
    # Initialize client
    client = TelegramClient('member_session', API_ID, API_HASH)
    
    try:
        # Connect and login
        client.connect()
        
        if not client.is_user_authorized():
            print("\n\033[1;33m=== LOGIN REQUIRED ===\033[0m")
            phone = input("\033[1;34mEnter phone number (with country code): + \033[0m")
            
            # Send code request
            try:
                client.send_code_request(phone)
                code = input("\033[1;34mEnter the 5-digit code you received: \033[0m")
                
                # Sign in
                try:
                    client.sign_in(phone, code)
                except SessionPasswordNeededError:
                    pw = input("\033[1;34mEnter your 2FA password: \033[0m")
                    client.sign_in(password=pw)
                
                print("\n\033[1;32m✓ Login successful!\033[0m")
            except Exception as e:
                print(f"\033[1;31m❌ Error during login: {e}\033[0m")
                return
        
        # Channel selection
        print("\n\033[1;33m=== CHANNEL SELECTION ===\033[0m")
        while True:
            try:
                source = input("\033[1;34mEnter SOURCE channel username (@name): \033[0m").strip('@')
                target = input("\033[1;34mEnter TARGET channel username (@yourchannel): \033[0m").strip('@')
                
                # Get channel entities
                source_entity = client.get_entity(source)
                target_entity = client.get_entity(target)
                
                # Confirmation
                print(f"\n\033[1;35mSource: {source_entity.title} (ID: {source_entity.id})")
                print(f"Target: {target_entity.title} (ID: {target_entity.id})\033[0m")
                confirm = input("\n\033[1;33mConfirm transfer? (y/n): \033[0m").lower()
                if confirm == 'y':
                    break
                else:
                    print("\033[1;33mRestarting channel selection...\033[0m")
                    
            except (UsernameNotOccupiedError, ValueError):
                print("\033[1;31m❌ Channel not found. Check the username!\033[0m")
            except ChannelPrivateError:
                print("\033[1;31m❌ You don't have access to this channel!\033[0m")
        
        # Get members
        print("\n\033[1;33mFetching members from source channel...\033[0m")
        all_users = []
        try:
            for user in client.iter_participants(source_entity):
                if not user.bot and not user.deleted:
                    all_users.append(user)
            print(f"\033[1;32m✓ Found {len(all_users)} valid members\033[0m")
        except Exception as e:
            print(f"\033[1;31m❌ Error fetching members: {e}\033[0m")
            return
        
        # Transfer process
        print("\n\033[1;33m=== STARTING TRANSFER ===\033[0m")
        print("\033[1;33mPress Ctrl+C to stop at any time\033[0m\n")
        
        added_count = 0
        skipped_count = 0
        error_count = 0
        batch_size = 5  # Safe for mobile
        
        for i in range(0, len(all_users), batch_size):
            batch = all_users[i:i + batch_size]
            
            try:
                # Attempt to add users
                client(InviteToChannelRequest(
                    target_entity,
                    batch
                ))
                added_count += len(batch)
                print(f"\033[1;32m✓ Success: Added {len(batch)} users (Total: {added_count})\033[0m")
                
                # Delay between batches
                wait_time = 30
                print(f"\033[1;34mWaiting {wait_time} seconds...\033[0m", end='\r')
                time.sleep(wait_time)
                print(" "*50, end='\r')
                
            except FloodWaitError as fwe:
                wait = fwe.seconds + 10
                print(f"\033[1;31m⏳ Flood wait detected. Waiting {wait} seconds...\033[0m")
                time.sleep(wait)
                continue
            except PeerFloodError:
                print("\033[1;31m❌ Telegram blocked you for adding too many users. Try again tomorrow.\033[0m")
                break
            except UserPrivacyRestrictedError:
                skipped_count += len(batch)
                print(f"\033[1;33m⚠ Skipped {len(batch)} users (privacy restrictions)\033[0m")
                continue
            except Exception as e:
                error_count += len(batch)
                print(f"\033[1;31m⚠ Error with batch: {e}\033[0m")
                time.sleep(10)
                continue
        
        # Final report
        print("\n\033[1;36m" + "="*50)
        print(" TRANSFER COMPLETE ")
        print("="*50 + "\033[0m")
        print(f"\033[1;32mSuccessfully added: {added_count}\033[0m")
        print(f"\033[1;33mSkipped (restrictions): {skipped_count}\033[0m")
        print(f"\033[1;31mErrors encountered: {error_count}\033[0m")
        print(f"\033[1;35mTotal processed: {len(all_users)}\033[0m")
        
    except KeyboardInterrupt:
        print("\n\033[1;33mProcess stopped by user\033[0m")
    except Exception as e:
        print(f"\033[1;31m❌ Fatal error: {e}\033[0m")
    finally:
        client.disconnect()
        print("\n\033[1;36mSession ended. Safe to close.\033[0m")

if __name__ == '__main__':
    main()