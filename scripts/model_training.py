import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from frame_interpolator import FrameInterpolator
from dataset_manager import FrameInterpolationDataset
from sklearn.model_selection import train_test_split

def main():
    # Set up hyperparameters for training
    num_epochs = 10  # Number of training epochs
    batch_size = 16  # Number of samples per batch
    learning_rate = 0.001  # Learning rate for the optimizer

    # Load the dataset and split it into training and testing sets
    dataset = FrameInterpolationDataset(directory="./data/processed_frames")
    train_size = int(0.8 * len(dataset))  # 80% of the dataset for training
    test_size = len(dataset) - train_size  # 20% for testing
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

    # Create DataLoader objects for iterating over the train and test sets
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)

    # Initialize the model and transfer it to the GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = FrameInterpolator().to(device)

    # Define the loss function (Mean Squared Error Loss) and optimizer (Adam)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Load the model checkpoint if it exists to resume training
    checkpoint_path = './models/frame_interpolator_checkpoint.pth'
    if os.path.isfile(checkpoint_path):
        checkpoint = torch.load(checkpoint_path)
        start_epoch = checkpoint['epoch']
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        print(f"Loaded checkpoint from epoch {start_epoch}")

    # Begin the training process
    for epoch in range(num_epochs):
        model.train()  # Set the model to training mode
        total_train_loss = 0  # Accumulate total loss for the epoch

        # Iterate over batches of data in the training set
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)  # Transfer data to the GPU

            # Perform forward pass and calculate loss
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            total_train_loss += loss.item()

            # Perform backward pass and optimization step
            optimizer.zero_grad()  # Clear previous gradients
            loss.backward()  # Compute gradients
            optimizer.step()  # Update weights

            # Clear any cached memory to avoid CUDA out of memory errors
            torch.cuda.empty_cache()

        # Compute the average training loss for the epoch
        avg_train_loss = total_train_loss / len(train_loader)

        # Evaluate the model on the test set
        model.eval()  # Set the model to evaluation mode
        total_val_loss = 0  # Accumulate total validation loss

        # Disable gradient calculations for validation to save memory and computations
        with torch.no_grad():
            for inputs, targets in test_loader:
                inputs, targets = inputs.to(device), targets.to(device)  # Transfer data to the GPU

                # Perform forward pass and calculate loss
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                total_val_loss += loss.item()

        # Compute the average validation loss for the epoch
        avg_val_loss = total_val_loss / len(test_loader)

        # Print training and validation loss statistics
        print(f'Epoch [{epoch+1}/{num_epochs}], Training Loss: {avg_train_loss:.4f}, Validation Loss: {avg_val_loss:.4f}')

        # Save the model checkpoint at regular intervals
        torch.save({
            'epoch': epoch + 1,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': loss,
        }, checkpoint_path)

    # Save the final trained model
    torch.save(model.state_dict(), './models/frame_interpolator_final.pth')

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
