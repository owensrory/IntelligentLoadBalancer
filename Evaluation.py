import csv
import matplotlib.pyplot as plt


class Evaluation:
    
    def log_response_time(request_id, response_time):
        with open('response_times_2servers_no_autoscaling_80reqs.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([request_id, response_time])
            
            
    def read_response_times(self, filename):
        response_times = []
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                response_times.append(float(row[1]))
        return response_times

    def plot_response_times(self, filenames):
        plt.figure(figsize=(10, 6))  # Set the figure size as needed

        for filename in filenames:
            response_times = self.read_response_times(filename)
            plt.plot(response_times, label=filename.split('.')[0])  # Splitting to get a cleaner label

        plt.title('Response Times Comparison')
        plt.xlabel('Request Number')
        plt.ylabel('Response Time (seconds)')
        plt.legend()  # Add a legend to distinguish the lines
        plt.show()

# If this file is run directly, perform the evaluation
if __name__ == '__main__':
    evaluation = Evaluation()
    filenames = [
        'response_times_2servers_autoscaling_80reqs.csv',
        'response_times_2servers_no_autoscaling_80reqs.csv'
    ]
    evaluation.plot_response_times(filenames)