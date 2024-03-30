from PIL import Image

# file_names = ["frame_000000593.png", "frame_000000601.png", "frame_000000609.png", "frame_000000617.png", "frame_000000625.png", "frame_000000633.png", "frame_000000641.png", "frame_000000649.png", "frame_000000689.png", "frame_000000697.png", "frame_000000705.png", "frame_000000713.png", "frame_000000721.png", "frame_000000729.png", "frame_000000737.png", "frame_000000745.png", "frame_000000753.png", "frame_000000761.png", "frame_000000769.png", "frame_000000777.png", "frame_000000785.png", "frame_000000793.png", "frame_000000801.png", "frame_000000809.png", "frame_000000817.png", "frame_000000825.png",
#               "frame_000000857.png", "frame_000000865.png", "frame_000000873.png", "frame_000000881.png", "frame_000000889.png", "frame_000000897.png", "frame_000000905.png", "frame_000000913.png", "frame_000000921.png", "frame_000000929.png", "frame_000000937.png", "frame_000000945.png", "frame_000000953.png", "frame_000000961.png", "frame_000000969.png", "frame_000000977.png", "frame_000000985.png", "frame_000000993.png", "frame_000001001.png", "frame_000001009.png", "frame_000001017.png", "frame_000001025.png", "frame_000001033.png", "frame_000001041.png", "frame_000001049.png", "frame_000001057.png"]

file_names = ["frame_000001353.png", "frame_000001361.png", "frame_000001369.png", "frame_000001377.png", "frame_000001385.png", "frame_000001393.png", "frame_000001433.png", "frame_000001441.png", "frame_000001449.png", "frame_000001457.png", "frame_000001465.png", "frame_000001473.png", "frame_000001481.png", "frame_000001489.png", "frame_000001497.png", "frame_000001505.png", "frame_000001513.png", "frame_000001521.png", "frame_000001529.png", "frame_000001537.png", "frame_000001545.png", "frame_000001553.png", "frame_000001561.png", "frame_000001569.png", "frame_000001577.png", "frame_000001585.png",
              "frame_000001593.png", "frame_000001601.png", "frame_000001609.png", "frame_000001617.png", "frame_000001625.png", "frame_000001633.png", "frame_000001665.png", "frame_000001673.png", "frame_000001681.png", "frame_000001689.png", "frame_000001697.png", "frame_000001705.png", "frame_000001713.png", "frame_000001721.png", "frame_000001729.png", "frame_000001737.png", "frame_000001745.png", "frame_000001753.png", "frame_000001761.png", "frame_000001769.png", "frame_000001777.png", "frame_000001785.png", "frame_000001793.png", "frame_000001801.png", "frame_000001809.png", "frame_000001817.png", "frame_000001825.png"]
folder_path = "/mnt/RawInternalDatasets/karagag/Fujinon/VK/no_object/images/"

for name in file_names:
    im = Image.open(folder_path+name)
    im = im.crop((0, 0, 1278, 1080))
    im.save(folder_path+name)
