import sys
import time
import matplotlib.pyplot as plt
import numpy as np
from google.colab import files
np.set_printoptions(threshold=sys.maxsize)

array = np.fromfile("/2023-06-01-67.trace", np.int32)

#print(array)

# xaxis_sum =0
# for i in array[2:]:
#   xaxis_sum += array[i]
# print(xaxis_sum)

xaxis_sum = 0
yaxis = [0]
xaxis = [0]
for i in range(2, len(array)):
  xaxis_sum = xaxis_sum + array[i]
  #print(array[i])
  #print(xaxis_sum)
  xaxis.append(xaxis_sum)
  if i%2 == 0:
    yaxis.append(1)
  else:
    yaxis.append(0)



print(xaxis)
print(yaxis)

xaxis_updated = []
for i in range(len(xaxis)):
  xaxis_updated.append(xaxis[i]*array[0]*0.000001)

x_rounded_values = [round(value, 3) for value in xaxis_updated]
print(x_rounded_values)

print(sum(x_rounded_values[500:1000]))

print(len(x_rounded_values))
print(len(yaxis))

# plt.rcParams["figure.autolayout"] = True
# plt.rcParams["figure.figsize"] = (50, 10)
plt.rcParams.update({'font.size': 20})
plt.step(x_rounded_values[0:20], yaxis[0:20] )
plt.xlabel("Time length (in seconds)")
plt.ylabel("Status of RADAR Occupation")
plt.xticks(x_rounded_values[0:20], rotation=60, ha='right')
plt.yticks([0,1])
plt.xlim([0, max(x_rounded_values[0:20])+0.5])
plt.ylim([0, max(yaxis[0:20])+0.5])
#plt.savefig("img.svg")
plt.show()




num_bins = 10000

# Use the histogram function to bin the data
count, bin_edges = np.histogram(array[2:], bins=num_bins)

# finding the PDF of the histogram using count values
pdf = count / sum(count)

# using numpy np.cumsum to calculate the CDF
# We can also find using the PDF values by looping and adding
cdf = np.cumsum(pdf)

plt.plot(bin_edges[1:], cdf, label="CDF")
plt.xlim(0,50)
plt.title('RADAR timestamps')
plt.rcParams["figure.figsize"] = (10, 5)
#plt.xticks(np.arange(2000, 2700, 100))
plt.show()

nodeB_url = "http://${NEXRAN_XAPP}:8000/v1/nodebs/enB_macro_001_001_00019b"

current=time.time()
i_updated_min=0
i_updated_max=0
# sleep_timer=0;
bash_script_content = "#!/bin/bash\n"
bash_script_filename = "curl_command.sh"

curl_command = "curl -i -X PUT -H \"Content-type: application/json\" -d '{{\"ul_mask_sched\":[{}]}}' {}"

json_objects = []


def curl(i_updated_min, i_updated_max):
  global bash_script_content
  global bash_script_filename
  global json_objects
  sleep_timer = 0
  json_objects = []
  json_payload = ""
  final_curl_command = ""
  for i in range(i_updated_min, i_updated_max):

      sleep_timer = x_rounded_values[i+1]-x_rounded_values[i]

      if i % 2 == 0:
        mask = "0x000fff0"
      else:
        mask = "0x0000000"

      if i == i_updated_max-1 and mask == "0x0000000":
        start_time = '\'`echo "import time; current=time.time(); print(current+' + str(x_rounded_values[i]) + ' )" | python`\''
        end_time = '\'`echo "import time; current=time.time(); print(current+' + str(x_rounded_values[i+1]) + ')" | python`\''
        json_objects.append('{{"mask":"{}","start":{},"end":{}}}'.format(mask, start_time, end_time))
      else:
        start_time = '\'`echo "import time; current=time.time(); print(current+' + str(x_rounded_values[i]) + ' )" | python`\''
        end_time = '\'`echo "import time; current=time.time(); print(current+' + str(x_rounded_values[i+1]) + ')" | python`\''
        json_objects.append('{{"mask":"{}","start":{},"end":{}}}'.format(mask, start_time, end_time))
      #json_objects.append('{{"mask":"{}","start":{},"end":{}}}'.format(mask, start_time, end_time))
  json_payload = ",".join(json_objects)
  final_curl_command = curl_command.format(json_payload, nodeB_url)

  #print(final_curl_command)

  bash_script_content += f"{final_curl_command}\n"

  #print("sleep timer is ", sleep_timer)
  bash_script_content += f"sleep {sleep_timer}\n"
  return i_updated_min


for i in range (int(len(xaxis)/20)+1):
  if i_updated_min >= len(x_rounded_values) - (len(x_rounded_values)%20):
    curl(i_updated_min, i_updated_min+(len(x_rounded_values)%20)-19)
  else:
    curl(i_updated_min, i_updated_min+20)
    i_updated_min = i_updated_min + 20


bash_script_filename = "curl_command.sh"
with open(bash_script_filename, "w") as bash_script_file:
  bash_script_file.write(bash_script_content)

print(f"Bash script generated: {bash_script_filename}")
files.download(bash_script_filename)

# New Section
