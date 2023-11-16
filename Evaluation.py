import csv
import matplotlib.pyplot as plt


class Evaluation:
    
    def log_response_time(request_id, response_time):
        with open('response_times.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([request_id, response_time])
            
            
    def read_response_times(self):
        response_times = []
        with open('response_times.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                # Assuming the response time is the second element in each row
                response_times.append(float(row[1]))
        return response_times

    def plot_response_times(self):
        response_times = self.read_response_times()
        plt.plot(response_times)
        plt.title('Response Times')
        plt.xlabel('Request Number')
        plt.ylabel('Response Time (seconds)')
        plt.show()
    